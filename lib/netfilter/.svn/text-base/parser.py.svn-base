# -*- coding: utf-8 -*-
# 
# python-netfilter - Python modules for manipulating netfilter rules
# Copyright (C) 2007-2009 Bolloré Telecom
# See AUTHORS file for a full list of contributors.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import re
import sys
import types
from UserDict import UserDict

import netfilter.rule

# define useful regexps
re_table = re.compile(r'^\*(.*)$')
re_chain = re.compile(r'^:*([^\s]+) ([^\s]+) \[([0-9]+):([0-9]+)\]$')
re_rule = re.compile(r'^\[([0-9]+):([0-9]+)\] (.*)$')
re_quoted = re.compile(r'^"([^"]*)"$')
re_word = re.compile(r'("[^"]*"|[^\s]+)')
re_main_opt = re.compile(r'^-([^-])$')

class odict(UserDict):
	def __init__(self, dict = None):
		self._keys = []
		UserDict.__init__(self, dict)

	def __setitem__(self, key, item):
		UserDict.__setitem__(self, key, item)
		if key not in self._keys: self._keys.append(key)

 	def keys(self):
		return self._keys
	
	def iteritems(self):
		for k in self._keys:
			yield k, self[k]

class ParseError(Exception):
	pass

def split_words(line):
	def unquote(x): return re_quoted.sub(r'\1', x)
	return map(unquote, re_word.findall(line))

def pull_extension_opts(bits, pos):
	opt_bits = []
	inv = False
	while pos < len(bits) and not re_main_opt.match(bits[pos]):
		opt_bits.append(bits[pos])
		pos += 1
	return opt_bits, pos

def pull_main_opt(bits, pos):
	val = bits[pos]
	pos += 1
	if val == '!':
		val += ' ' + bits[pos]
		pos += 1
	return val, pos

def parse_rule(spec):
	rule = netfilter.rule.Rule()
	bits = split_words(spec)
	pos = 0
	append = None
	while pos < len(bits):
		bit = bits[pos]
		pos += 1
		if bit == '-A':
			append = bits[pos]
			pos += 1
		elif bit == '-d':
			rule.destination, pos = pull_main_opt(bits, pos)
		elif bit == '-i':
			rule.in_interface, pos = pull_main_opt(bits, pos)
		elif bit == '-g':
			target_name = bits[pos]
			opts, pos = pull_extension_opts(bits, pos + 1)
			rule.goto = netfilter.rule.Target(target_name, opts)
		elif bit == '-j':
			target_name = bits[pos]
			opts, pos = pull_extension_opts(bits, pos + 1)
			rule.jump = netfilter.rule.Target(target_name, opts)
		elif bit == '-m':
			match_name = bits[pos]
			opts, pos = pull_extension_opts(bits, pos + 1) 
			rule.matches.append(
				netfilter.rule.Match(match_name, opts))
		elif bit == '-o':
			rule.out_interface, pos = pull_main_opt(bits, pos)
		elif bit == '-p':
			rule.protocol, pos = pull_main_opt(bits, pos)
		elif bit == '-s':
			rule.source, pos = pull_main_opt(bits, pos)
		else:
			raise ParseError("unhandled option '%s' in rule '%s'" % (bit, spec))
	if not append:
		raise ParseError("no 'APPEND' found in rule '%s'" % spec)
	return append, rule

def parse_tables(ilines):
	# strip comments, empty lines and end of lines
	lines = []
	for line in ilines:
		if not re.match(r'^#', line) and not re.match(r'^\s*$', line):
			lines.append(line.strip())

	# parse remaining lines
	pos = 0
	tables = odict()
	while pos < len(lines) and re_table.match(lines[pos]):
		m = re_table.match(lines[pos])
		pos += 1
		tablename = m.group(1)

		tables[tablename] = odict()
		# parse chain definitions
		while pos < len(lines) and re_chain.match(lines[pos]):
			m = re_chain.match(lines[pos])
			pos += 1
			policy = None
			if m.group(2) != '-':
				policy = m.group(2)
			tables[tablename][m.group(1)] = {
				'policy': policy,
				'packets': int(m.group(3)),
				'bytes': int(m.group(4)),
				'rules': [],
			}

		# parse rule definitions
		while pos < len(lines) and re_rule.match(lines[pos]):
			m = re_rule.match(lines[pos])
			pos += 1
			chain, rule = parse_rule(m.group(3))
			rule.packets = int(m.group(1))
			rule.bytes = int(m.group(2))
			tables[tablename][chain]['rules'].append(rule)

		# skip COMMIT
		if lines[pos] != 'COMMIT':
			raise ParseError("expected COMMIT in line '%s'" % lines[pos])
		pos += 1
	
	# check we parsed everything
	if (pos < len(lines)):
		raise ParseError("expected table in line '%s'" % lines[pos])
	return tables

def dump_tables(tables):
	lines = []
	for table, chains in tables.iteritems():
		lines.append("*%s" % table)
		rules = []
		for chain, props in chains.iteritems():
			policy = '-'
			if props['policy']:
				policy = props['policy']
			lines.append(":%s %s [%i:%i]" % (chain, policy, props['packets'], props['bytes']))
			for rule in props['rules']:
				rule.chain = chain
				rules.append(rule)
		for rule in rules:
			lines.append("[%i:%i] -A %s %s" % (rule.packets, rule.bytes, rule.chain, ' '.join(rule.specbits())))
		lines.append("COMMIT")
	return lines

if __name__ == '__main__':
	import sys
	
	if len(sys.argv) < 2:
		print "syntax: %s filename" % sys.argv[0]
		sys.exit(1)

	filename = sys.argv[1]
	infile = open(filename, 'r')
	lines = infile.readlines()
	infile.close()

	tables = parse_tables(lines)
	lines = netfilter.parser.dump_tables(tables)
	for line in lines:
		print line

