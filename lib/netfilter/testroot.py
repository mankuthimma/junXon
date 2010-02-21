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

import netfilter.table
import netfilter.rule

# THESE TESTS NEED TO BE RUN AS ROOT, RUN WITH CARE

class TableManipulationTestCase(unittest.TestCase):
	def setUp(self, auto_commit = True):
		self.table = netfilter.table.Table('filter', auto_commit)
		self.chain = 'netfilter_test'
		self.table.create_chain(self.chain)
		self.table.flush_chain(self.chain)
	
	def tearDown(self):
		self.table.flush_chain(self.chain)
		self.table.delete_chain(self.chain)
	
class BasicTableTestCase(TableManipulationTestCase):
	def testCreateFindDeleteChain(self):
		# check the chain has 0 rules
		rules = self.table.list_rules(self.chain)
		self.assertEqual(len(rules), 0)
		
		# append a rule and check the chain has 1 rule
		rule = netfilter.rule.Rule(source='192.168.1.2', destination='192.168.1.3',
			jump='ACCEPT')
		self.table.append_rule(self.chain, rule)
		rules = self.table.list_rules(self.chain)
		self.assertEqual(len(rules), 1)
		
		# lookup the rule we added
		rule2 = rule.find(rules)
		self.assertEqual(rule2.source, '192.168.1.2')
		self.assertEqual(rule2.destination, '192.168.1.3')
		self.assertEqual(rule2.jump, netfilter.rule.Target('ACCEPT'))
	
		# delete the rule and check the chain has 0 rules
		self.table.delete_rule(self.chain, rule)
		rules = self.table.list_rules(self.chain)
		self.assertEqual(len(rules), 0)

	def testCreateFlushChain(self):
		# check the chain has 0 rules
		rules = self.table.list_rules(self.chain)
		self.assertEqual(len(rules), 0)
		
		# append a rule and check the chain has 1 rule
		rule = netfilter.rule.Rule(source='192.168.1.2', destination='192.168.1.3',
			jump='ACCEPT')
		self.table.append_rule(self.chain, rule)
		rules = self.table.list_rules(self.chain)
		self.assertEqual(len(rules), 1)
		
		# empty the chain and check the chain has 0 rules
		self.table.flush_chain(self.chain)
		rules = self.table.list_rules(self.chain)
		self.assertEqual(len(rules), 0)

	def testRenameChain(self):
		new_chain = self.chain + '_new'
		
		# append a rule and check the chain has 1 rule
		rule = netfilter.rule.Rule(source='192.168.1.2', destination='192.168.1.3',
			jump='ACCEPT')
		self.table.append_rule(self.chain, rule)
		rules = self.table.list_rules(self.chain)
		self.assertEqual(len(rules), 1)
		
		# rename chain
		self.table.rename_chain(self.chain, new_chain)
		rules = self.table.list_rules(new_chain)
		self.assertEqual(len(rules), 1)

		# rename chain back
		self.table.rename_chain(new_chain, self.chain)
		rules = self.table.list_rules(self.chain)
		self.assertEqual(len(rules), 1)

class BufferTestCase(TableManipulationTestCase):
	def setUp(self):
		TableManipulationTestCase.setUp(self, False)
		
	def testfoo(self):
		self.assertEqual(self.table.get_buffer(), [['iptables', '-t', 'filter', '-N', 'netfilter_test'], ['iptables', '-t', 'filter', '-F', 'netfilter_test']])

if __name__ == '__main__':
	unittest.main()
