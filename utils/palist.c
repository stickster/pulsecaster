/*
 * palist.c - List sinks and/or sources available on a PulseAudio server
 *
 * This file is licensed under terms of the GNU General Public License
 * (GPL), either version 2 or (at your option) any later version.  No
 * warranty is herein expressed or implied.  Refer to the GNU GPL for
 * more details.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <errno.h>
#include <unistd.h>
#include <limits.h>
#include <assert.h>
#include <getopt.h>

#include <pulse/pulseaudio.h>

static pa_context *context = NULL;
static pa_mainloop_api *mainloop_api = NULL;

static int verbose = 0;
static int actions = 1;

static enum {
  NONE,
  LIST_SOURCES,
  LIST_SINKS,
  LIST_ALL
} action = NONE;

static inline const char *pa_strnull(const char *x) {
  return x ? x : "(null)";
}

/* Shortcut to terminate */
static void quit(int ret) {
  assert(mainloop_api);
  mainloop_api->quit(mainloop_api, ret);
}

static void context_drain_complete(pa_context *c, void *userdata) {
  pa_context_disconnect(c);
}

static void drain(void) {
  pa_operation *o;
  if(!(o = pa_context_drain(context, context_drain_complete, NULL)))
    pa_context_disconnect(context);
  else
    pa_operation_unref(o);
}

static void complete_action(void) {
  assert(actions > 0);
  if(!(--actions))
    drain();
}

static void exit_signal_callback(pa_mainloop_api *m, pa_signal_event *e, int sig, void *userdata) {
    fprintf(stderr, "Got SIGINT, exiting.\n");
    quit(0);
}

static void get_source_list_callback(pa_context *c,
				     const pa_source_info *i,
				     int eol,
				     void *userdata) {
  if(eol < 0) {
    fprintf(stderr, "Failed to get source information: %s\n",
	    pa_strerror(pa_context_errno(c)));
    quit(1);
    return;
  }

  if(eol) {
    complete_action();
    return;
  }
  
  assert(i);
  
  printf("Source #%u <%s> %s\n", i->index, i->name, pa_strnull(i->description));
}

static void get_sink_list_callback(pa_context *c,
				     const pa_sink_info *i,
				     int eol,
				     void *userdata) {
  if(eol < 0) {
    fprintf(stderr, "Failed to get sink information: %s\n",
	    pa_strerror(pa_context_errno(c)));
    quit(1);
    return;
  }

  if(eol) {
    complete_action();
    return;
  }
  
  assert(i);
  
  printf("Sink #%u <%s> %s\n", i->index, i->name, pa_strnull(i->description));
}

static void context_state_callback(pa_context *c, void *userdata) {
    assert(c);
    switch (pa_context_get_state(c)) {
    case PA_CONTEXT_CONNECTING:
    case PA_CONTEXT_AUTHORIZING:
    case PA_CONTEXT_SETTING_NAME:
      break;

    case PA_CONTEXT_READY:
      switch (action) {
      case LIST_SOURCES:
	pa_operation_unref(pa_context_get_source_info_list(c, get_source_list_callback, NULL));
	break;

      case LIST_SINKS:
	pa_operation_unref(pa_context_get_sink_info_list(c, get_sink_list_callback, NULL));
	break;

      case LIST_ALL:
	actions = 2;
	pa_operation_unref(pa_context_get_source_info_list(c, get_source_list_callback, NULL));
	pa_operation_unref(pa_context_get_sink_info_list(c, get_sink_list_callback, NULL));
	break;

      default:
	assert(0);
      }
      break;
      
    case PA_CONTEXT_TERMINATED:
      quit(0);
      break;

    case PA_CONTEXT_FAILED:
    default:
      fprintf(stderr, "Connection failure: %s\n",
	      pa_strerror(pa_context_errno(c)));
      quit(1);
    }
}


static void help(const char *argv0) {
  printf("%s [options]\n"
	 "  -h                        Show this help\n"
	 "  -c, --list-sources        List sources\n"
	 "  -k, --list-sinks          List sinks\n"
	 "  -a, --list-all            List sources and sinks\n",
	 argv0);
}


/* ----------- MAIN ------------ */
int main(int argc, char *argv[]) {
  pa_mainloop* m = NULL;
  char *server = NULL;
  char *client_name = NULL;
  int ret = 1, r, c;

  static const struct option long_options[] = {
    {"help", 0, NULL, 'h'},
    {"list-sources", 0, NULL, 'c'},
    {"list-sinks", 0, NULL, 'k'},
    {"list-all", 0, NULL, 'a'},
    {NULL, 0, NULL, 0}
  };

  client_name = pa_xstrdup("palist");  // Make this more flexible later;

  while ((c = getopt_long(argc, argv, "ckah", long_options, NULL)) != -1) {
    switch (c) {
    case 'h':
      help(client_name);
      ret = 0;
      goto quit;

    case 'c':
      action = LIST_SOURCES;
      break;

    case 'k':
      action = LIST_SINKS;
      break;

    case 'a':
      action = LIST_ALL;
      break;
      
    default:
      goto quit;
    }
  }

  if (action == NONE) {
    fprintf(stderr, "No valid option specified\n");
    goto quit;
  }

  if (!(m = pa_mainloop_new())) {
    fprintf(stderr, "pa_mainloop_new() failed.\n");
    goto quit;
  }

  mainloop_api = pa_mainloop_get_api(m);
  
  r = pa_signal_init(mainloop_api);
  assert(r == 0);
  pa_signal_new(SIGINT, exit_signal_callback, NULL);
#ifdef SIGPIPE
  signal(SIGPIPE, SIG_IGN);
#endif

  if (!(context = pa_context_new(mainloop_api, client_name))) {
    fprintf(stderr, "pa_context_new() failed.\n");
    goto quit;
  }

  pa_context_set_state_callback(context, context_state_callback, NULL);
  if (pa_context_connect(context, server, 0, NULL) < 0) {
    fprintf(stderr, "pa_context_connect() failed: %s", pa_strerror(pa_context_errno(context)));
    goto quit;
  }
  
  if (pa_mainloop_run(m, &ret) < 0) {
    fprintf(stderr, "pa_mainloop_run() failed.\n");
    goto quit;
  }

quit:
  if (context)
    pa_context_unref(context);
  
  if (m) {
    pa_signal_done();
    pa_mainloop_free(m);
  }
  
  pa_xfree(client_name);
  
  return ret;
}
