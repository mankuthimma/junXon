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

import unittest
import logging

import netfilter.table
from netfilter.rule import Rule,Target,Match
import netfilter.parser

class ParserTestCase(unittest.TestCase):
	def testSplitWords(self):
		line = 'a b c'
		self.assertEqual(netfilter.parser.split_words(line),
			['a', 'b', 'c'])

	def testSplitWordsQuoted(self):
		line = 'a "some text" b'
		self.assertEqual(netfilter.parser.split_words(line),
			['a', 'some text', 'b'])

class TargetTestCase(unittest.TestCase):
	def testInit(self):
		target = Target('ACCEPT')
		self.assertEqual(target.name(), 'ACCEPT')
		self.assertEqual(target.options(), {})

	def testInitOptions(self):
		target = Target('REDIRECT', '--wiz bang --foo bar')
		self.assertEqual(target.name(), 'REDIRECT')
		self.assertEqual(target.options(), {'foo': ['bar'], 'wiz': ['bang']})

	def testEqual(self):
		target1 = Target('ACCEPT', '--foo bar')
		target2 = Target('ACCEPT', '--foo bar')
		self.assertEqual(target1 == target2, True)
		self.assertEqual(target1 != target2, False)
	
	def testEqualOutOfOrder(self):
		target1 = Target('ACCEPT', '--foo bar --wiz bang')
		target2 = Target('ACCEPT', '--wiz bang --foo bar')
		self.assertEqual(target1 == target2, True)
		self.assertEqual(target1 != target2, False)

	def testNotEqualName(self):
		target1 = Target('ACCEPT', '--foo bar')
		target2 = Target('ACCEPT2', '--foo bar')
		self.assertEqual(target1 == target2, False)
		self.assertEqual(target1 != target2, True)

	def testNotEqualOptions(self):
		target1 = Target('ACCEPT')
		target2 = Target('ACCEPT', '--foo bar')
		self.assertEqual(target1 == target2, False)
		self.assertEqual(target1 != target2, True)

class MatchTestCase(unittest.TestCase):
	def testRewriteSourcePort(self):
		match = Match('tcp', '--source-port 1234')
		self.assertEqual(match.options(), {'sport': ['1234']})
	
	def testRewriteSourcePorts(self):
		match = Match('multiport', '--source-ports 1,2,3')
		self.assertEqual(match.options(), {'sports': ['1,2,3']})
	
	def testRewriteDestPorts(self):
		match = Match('tcp', '--destination-port 1234')
		self.assertEqual(match.options(), {'dport': ['1234']})
	
	def testRewriteDestPorts(self):
		match = Match('multiport', '--destination-ports 1,2,3')
		self.assertEqual(match.options(), {'dports': ['1,2,3']})

class RuleTestCase(unittest.TestCase):
	def testInit(self):
		rule = Rule(jump=Target('ACCEPT'))
		self.assertEqual(rule.protocol, None)
		self.assertEqual(rule.in_interface, None)
		self.assertEqual(rule.out_interface, None)
		self.assertEqual(rule.source, None)
		self.assertEqual(rule.destination, None)
		self.assertEqual(rule.jump.name(), 'ACCEPT')
		self.assertEqual(rule.jump.options(), {})
		self.assertEqual(rule.specbits(), ['-j', 'ACCEPT'])
	
	def testSource(self):
		rule = Rule(source='192.168.1.2', jump='ACCEPT')
		self.assertEqual(rule.protocol, None)
		self.assertEqual(rule.in_interface, None)
		self.assertEqual(rule.out_interface, None)
		self.assertEqual(rule.source, '192.168.1.2')
		self.assertEqual(rule.destination, None)
		self.assertEqual(rule.jump.name(), 'ACCEPT')
		self.assertEqual(rule.jump.options(), {})
		self.assertEqual(rule.specbits(), ['-s', '192.168.1.2', '-j', 'ACCEPT'])

	def testDestination(self):
		rule = Rule(destination='192.168.1.3', jump='REJECT')
		self.assertEqual(rule.protocol, None)
		self.assertEqual(rule.in_interface, None)
		self.assertEqual(rule.out_interface, None)
		self.assertEqual(rule.source, None)
		self.assertEqual(rule.destination, '192.168.1.3')
		self.assertEqual(rule.jump.name(), 'REJECT')
		self.assertEqual(rule.jump.options(), {})
		self.assertEqual(rule.specbits(), ['-d', '192.168.1.3', '-j', 'REJECT'])
	
	def testSourceDestinationProtocol(self):
		rule = Rule(source='192.168.1.2', destination='192.168.1.3',
			protocol='tcp', jump='DROP')
		self.assertEqual(rule.protocol, 'tcp')
		self.assertEqual(rule.in_interface, None)
		self.assertEqual(rule.out_interface, None)
		self.assertEqual(rule.source, '192.168.1.2')
		self.assertEqual(rule.destination, '192.168.1.3')
		self.assertEqual(rule.jump.name(), 'DROP')
		self.assertEqual(rule.jump.options(), {})
		self.assertEqual(rule.specbits(), ['-p', 'tcp', '-s', '192.168.1.2', '-d', '192.168.1.3', '-j', 'DROP'])

	def testInterfaces(self):
		rule = Rule(in_interface='eth1', out_interface='eth2',
			jump='REJECT')
		self.assertEqual(rule.protocol, None)
		self.assertEqual(rule.in_interface, 'eth1')
		self.assertEqual(rule.out_interface, 'eth2')
		self.assertEqual(rule.source, None)
		self.assertEqual(rule.destination, None)
		self.assertEqual(rule.specbits(), ['-i', 'eth1', '-o', 'eth2', '-j', 'REJECT'])
	
	def testTargetLog(self):
		rule = Rule(jump=Target('LOG', '--log-prefix "ICMP accepted : " --log-level 4'))
		self.assertEqual(rule.specbits(), ['-j', 'LOG', '--log-prefix', 'ICMP accepted : ', '--log-level', '4'])

	def testMatchMark(self):
		rule = Rule(jump='ACCEPT')
		rule.matches.append(Match('mark', '--mark 0x64'))
		self.assertEqual(rule.specbits(), ['-m', 'mark', '--mark', '0x64', '-j', 'ACCEPT'])

	def testMatchMultiportDports(self):
		rule = Rule(jump='ACCEPT')
		rule.matches.append(Match('multiport', '--dports 20,21,22,80,25,1720'))
		self.assertEqual(rule.specbits(), ['-m', 'multiport', '--dports', '20,21,22,80,25,1720', '-j', 'ACCEPT'])

	def testMatchState(self):
		rule = Rule(jump='ACCEPT')
		rule.matches.append(Match('state', '--state ESTABLISHED,RELATED'))
		self.assertEqual(rule.specbits(), ['-m', 'state', '--state', 'ESTABLISHED,RELATED', '-j', 'ACCEPT'])

	def testMatchTcpFlags(self):
		rule = Rule(protocol='tcp', jump='ACCEPT')
		rule.matches.append(Match('tcp', '--tcp-flags ACK,SYN ACK'))
		self.assertEqual(rule.specbits(), ['-p', 'tcp', '-m', 'tcp', '--tcp-flags', 'ACK,SYN', 'ACK', '-j', 'ACCEPT'])
	
	def testMatchTcpNotFlags(self):
		rule = Rule(protocol='tcp', jump='ACCEPT')
		rule.matches.append(Match('tcp', '--tcp-flags ! ACK,SYN ACK'))
		self.assertEqual(rule.specbits(), ['-p', 'tcp', '-m', 'tcp', '--tcp-flags', '!', 'ACK,SYN', 'ACK', '-j', 'ACCEPT'])

	def testMatchTcpDport(self):
		rule = Rule(protocol='tcp', jump='ACCEPT')
		rule.matches.append(Match('tcp', '--dport 80'))
		self.assertEqual(rule.specbits(), ['-p', 'tcp', '-m', 'tcp', '--dport', '80', '-j', 'ACCEPT'])

	def testMatchTcpSport(self):
		rule = Rule(protocol='tcp', jump='ACCEPT')
		rule.matches.append(Match('tcp', '--sport 1234'))
		self.assertEqual(rule.specbits(), ['-p', 'tcp', '-m', 'tcp', '--sport', '1234', '-j', 'ACCEPT'])

	def testMatchTos(self):
		rule = Rule(jump='ACCEPT')
		rule.matches.append(Match('tos', '--tos 0x10'))
		self.assertEqual(rule.specbits(), ['-m', 'tos', '--tos', '0x10', '-j', 'ACCEPT'])

class ParseRuleTestCase(unittest.TestCase):
	def testEmpty(self):
		append, rule = netfilter.parser.parse_rule('-A foo')
		self.assertEqual(append, 'foo')
		self.assertEqual(rule, Rule())
		self.assertEqual(rule.specbits(), [])
	
	def testGoto(self):
		append, rule = netfilter.parser.parse_rule('-A foo -g some_rule')
		self.assertEqual(append, 'foo')
		self.assertEqual(rule, Rule(goto='some_rule'))
		self.assertEqual(rule.specbits(), ['-g', 'some_rule'])

	def testJump(self):
		append, rule = netfilter.parser.parse_rule('-A foo -j REJECT')
		self.assertEqual(append, 'foo')
		self.assertEqual(rule, Rule(jump='REJECT'))
		self.assertEqual(rule.specbits(), ['-j', 'REJECT'])

	def testProtocol(self):
		append, rule = netfilter.parser.parse_rule('-A foo -p tcp')
		self.assertEqual(append, 'foo')
		self.assertEqual(rule, Rule(protocol='tcp'))
		self.assertEqual(rule.specbits(), ['-p', 'tcp'])

	def testMatch(self):
		append, rule = netfilter.parser.parse_rule('-A foo -m state --state ESTABLISHED,RELATED')
		self.assertEqual(append, 'foo')
		self.assertEqual(rule, Rule(
			matches=[Match('state', '--state ESTABLISHED,RELATED')]))
		self.assertEqual(rule.specbits(), ['-m', 'state', '--state', 'ESTABLISHED,RELATED'])
		
class BufferedTestCase(unittest.TestCase):
	def testJump(self):
		table = netfilter.table.Table('test_table', False)
		table.append_rule('test_chain', Rule(jump='ACCEPT'))
		buffer = table.get_buffer()
		self.assertEqual(buffer, [['iptables', '-t', 'test_table', '-A', 'test_chain', '-j', 'ACCEPT']])

if __name__ == '__main__':
	unittest.main()
