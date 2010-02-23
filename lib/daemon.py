# -*- coding: utf-8 -*-

## Copyright 2007-2008 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2007-2008 by Walter Dörwald
##
## All Rights Reserved
##
## See __init__.py for the license


ur"""
<p>This module can be used on UNIX to fork a daemon process. It is based
on <a href="http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012">Jürgen Hermann's Cookbook recipe</a>.</p>

<p>An example script might look like this:</p>

<example>
<prog>
from ll import daemon

counter = daemon.Daemon(
	stdin="/dev/null",
	stdout="/tmp/daemon.log",
	stderr="/tmp/daemon.log",
	pidfile="/var/run/counter/counter.pid",
	user="nobody"
)

if __name__ == "__main__":
	if counter.service():
		import sys, os, time
		sys.stdout.write("Daemon started with pid %d\n" % os.getpid())
		sys.stdout.write("Daemon stdout output\n")
		sys.stderr.write("Daemon stderr output\n")
		c = 0
		while True:
			sys.stdout.write('%d: %s\n' % (c, time.ctime(time.time())))
			sys.stdout.flush()
			c += 1
			time.sleep(1)
</prog>
</example>
"""


import sys, os, signal, pwd, grp, optparse


__docformat__ = "xist"


class Daemon(object):
	"""
	The <class>Daemon</class> class provides methods for <pyref method="start">starting</pyref>
	and <pyref method="stop">stopping</pyref> a daemon process as well as
	<pyref method="service">handling command line arguments</pyref>.
	"""
	def __init__(self, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null", pidfile=None, user=None, group=None):
		"""
		<p>The <arg>stdin</arg>, <arg>stdout</arg>, and <arg>stderr</arg> arguments
		are file names that will be opened and be used to replace the standard file
		descriptors in <lit>sys.stdin</lit>, <lit>sys.stdout</lit>, and
		<lit>sys.stderr</lit>. These arguments are optional and default to
		<lit>"/dev/null"</lit>. Note that stderr is opened unbuffered, so if it
		shares a file with stdout then interleaved output may not appear in the
		order that you expect.</p>

		<p><arg>pidfile</arg> must be the name of a file. <meth>start</meth>
		will write the pid of the newly forked daemon to this file. <meth>stop</meth>
		uses this file to kill the daemon.</p>

		<p><arg>user</arg> can be the name or uid of a user. <meth>start</meth>
		will switch to this user for running the service. If <arg>user</arg> is
		<lit>None</lit> no user switching will be done.</p>

		<p>In the same way <arg>group</arg> can be the name or gid of a group.
		<meth>start</meth> will switch to this group.</p>
		"""
		options = dict(
			stdin=stdin,
			stdout=stdout,
			stderr=stderr,
			pidfile=pidfile,
			user=user,
			group=group,
		)

		self.options = optparse.Values(options)

	def openstreams(self):
		"""
		Open the standard file descriptors stdin, stdout and stderr as specified
		in the constructor.
		"""
		si = open(self.options.stdin, "r")
		so = open(self.options.stdout, "a+")
		se = open(self.options.stderr, "a+", 0)
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())
	
	def handlesighup(self, signum, frame):
		"""
		Handle a <lit>SIG_HUP</lit> signal: Reopen standard file descriptors.
		"""
		self.openstreams()

	def handlesigterm(self, signum, frame):
		"""
		Handle a <lit>SIG_TERM</lit> signal: Remove the pid file and exit.
		"""
		if self.options.pidfile is not None:
			try:
				os.remove(self.options.pidfile)
			except (KeyboardInterrupt, SystemExit):
				raise
			except Exception:
				pass
		sys.exit(0)

	def switchuser(self, user, group):
		"""
		Switch the effective user and group. If <arg>user</arg> is <lit>None</lit>
		and <arg>group</arg> is nothing will be done. <arg>user</arg> and <arg>group</arg>
		can be an <class>int</class> (i.e. a user/group id) or <class>str</class>
		(a user/group name).
		"""
		if group is not None:
			if isinstance(group, basestring):
				group = grp.getgrnam(group).gr_gid
			os.setegid(group)
		if user is not None:
			if isinstance(user, basestring):
				user = pwd.getpwnam(user).pw_uid
			os.seteuid(user)
			if "HOME" in os.environ:
				os.environ["HOME"] = pwd.getpwuid(user).pw_dir

	def start(self):
		"""
		Daemonize the running script. When this method returns the process is
		completely decoupled from the parent environment.
		"""
		# Finish up with the current stdout/stderr
		sys.stdout.flush()
		sys.stderr.flush()
	
		# Do first fork
		try:
			pid = os.fork()
			if pid > 0:
				sys.exit(0) # Exit first parent
		except OSError, exc:
			sys.exit("%s: fork #1 failed: (%d) %s\n" % (sys.argv[0], exc.errno, exc.strerror))
	
		# Decouple from parent environment
		os.chdir("/")
		os.umask(0)
		os.setsid()
	
		# Do second fork
		try:
			pid = os.fork()
			if pid > 0:
				sys.exit(0) # Exit second parent
		except OSError, exc:
			sys.exit("%s: fork #2 failed: (%d) %s\n" % (sys.argv[0], exc.errno, exc.strerror))
	
		# Now I am a daemon!
	
		# Switch user
		self.switchuser(self.options.user, self.options.group)

		# Redirect standard file descriptors (will belong to the new user)
		self.openstreams()
	
		# Write pid file (will belong to the new user)
		if self.options.pidfile is not None:
			open(self.options.pidfile, "wb").write(str(os.getpid()))

		# Reopen file descriptions on SIGHUP
		signal.signal(signal.SIGHUP, self.handlesighup)

		# Remove pid file and exit on SIGTERM
		signal.signal(signal.SIGTERM, self.handlesigterm)

	def stop(self):
		"""
		Send a <lit>SIGTERM</lit> signal to a running daemon. The pid of the
		daemon will be read from the pidfile specified in the constructor.
		"""
		if self.options.pidfile is None:
			sys.exit("no pidfile specified")
		try:
			pidfile = open(self.options.pidfile, "rb")
		except IOError, exc:
			sys.stderr.write("Ignoring missing pidfile %s: %s\n" % (self.options.pidfile, str(exc)))
                        return -1
		data = pidfile.read()
		try:
			pid = int(data)
		except ValueError:
			sys.stderr.write("pidfile looks mangled %s: %r\n" % (self.options.pidfile, data))

                try:
                        os.kill(pid, signal.SIGTERM)
                except OSError:
                        sys.stderr.write("Ignoring missing PID\n")

	def optionparser(self):
		"""
		Return an <mod>optparse</mod> parser for parsing the command line options.
		This can be overwritten in subclasses to add more options.
		"""
		p = optparse.OptionParser(usage="usage: %prog [options] (start|stop|restart|run)")
		p.add_option("--pidfile", dest="pidfile", help="PID filename (default %default)", default=self.options.pidfile)
		p.add_option("--stdin", dest="stdin", help="stdin filename (default %default)", default=self.options.stdin)
		p.add_option("--stdout", dest="stdout", help="stdout filename (default %default)", default=self.options.stdout)
		p.add_option("--stderr", dest="stderr", help="stderr filename (default %default)", default=self.options.stderr)
		p.add_option("--user", dest="user", help="user name or id (default %default)", default=self.options.user)
		p.add_option("--group", dest="group", help="group name or id (default %default)", default=self.options.group)
		return p

	def service(self, args=None):
		"""
		<p>Handle command line arguments and start or stop the daemon accordingly.</p>

		<p><arg>args</arg> must be a list of command line arguments (including the
		program name in <lit>args[0]</lit>). If <arg>args</arg> is <lit>None</lit>
		or unspecified <lit>sys.argv</lit> is used.</p>

		<p>The return value is true, a starting option has been specified
		as the command line argument, i.e. if the daemon should be started.</p>

		<p>The <mod>optparse</mod> options and arguments are available
		afterwards as <lit><self/>.options</lit> and <lit><self/>.args</lit>.
		"""
		p = self.optionparser()
		if args is None:
			args = sys.argv
		(self.options, self.args) = p.parse_args(args)
		if len(self.args) != 2:
			p.error("incorrect number of arguments")
			sys.exit(1)
		if self.args[1] == "run":
			return True
		elif self.args[1] == "restart":
			self.stop()
			self.start()
			return True
		elif self.args[1] == "start":
			self.start()
			return True
		elif self.args[1] == "stop":
			self.stop()
			return False
		else:
			p.error("incorrect argument %s" % self.args[1])
			sys.exit(1)
