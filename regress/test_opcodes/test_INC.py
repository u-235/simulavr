#! /usr/bin/env python
###############################################################################
#
# simulavr - A simulator for the Atmel AVR family of microcontrollers.
# Copyright (C) 2001, 2002  Theodore A. Roth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
###############################################################################
#
# $Id: test_INC.py,v 1.1 2004/07/31 00:59:11 rivetwa Exp $
#

"""Test the INC opcode.
"""

import base_test
from registers import Reg, SREG

class INC_TestFail(base_test.TestFail): pass

class base_INC(base_test.opcode_test):
	"""Generic test case for testing INC opcode.

	INC - Increment
	opcode is '1001 010d dddd 0011' where 0 <= d <= 31

	Only registers PC, Rd and SREG should be changed.
	"""
	def setup(self):
		# Set SREG to zero
		self.setup_regs[Reg.SREG] = 0

		# Set the register values
		self.setup_regs[self.Rd] = self.Vd

		# Return the raw opcode
		return 0x9403 | (self.Rd << 4)

	def analyze_results(self):
		self.reg_changed.extend( [self.Rd, Reg.SREG] )
		
		# check that result is correct
		exp = (self.Vd + 1) & 0xff

		got = self.anal_regs[self.Rd]
		
		if exp != got:
			self.fail('INC r%02d: 0x%02x = (expect=%02x, got=%02x)' % (
				self.Rd, self.Vd, exp, got))

		expect_sreg = 0

		# calculate what we expect sreg to be (I, T, H and C should be zero)
		V = (self.Vd == 0x7f)
		N = ((exp & 0x80) != 0)
		expect_sreg += V          << SREG.V
		expect_sreg += N          << SREG.N
		expect_sreg += (N ^ V)    << SREG.S
		expect_sreg += (exp == 0) << SREG.Z

		got_sreg = self.anal_regs[Reg.SREG]

		if expect_sreg != got_sreg:
			self.fail('INC r%02d: 0x%02x -> SREG (expect=%02x, got=%02x)' % (
				self.Rd, self.Vd, expect_sreg, got_sreg))

#
# Template code for test case.
# The fail method will raise a test specific exception.
#
template = """
class INC_r%02d_v%02x_TestFail(INC_TestFail): pass

class test_INC_r%02d_v%02x(base_INC):
	Rd = %d
	Vd = 0x%x
	def fail(self,s):
		raise INC_r%02d_v%02x_TestFail, s
"""

#
# Define a list of test values such that we test all the cases of SREG bits being set.
#
vals = (
0x00,
0xff,
0xaa,
0xf0,
0x01,
0x7f,
0x80
)

#
# automagically generate the test_INC_rNN_vXX class definitions.
#
code = ''
for d in range(32):
	for vd in vals:
		args = (d,vd)*4
		code += template % args

exec code
