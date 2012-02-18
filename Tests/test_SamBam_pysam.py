# Copyright 2010-2012 by Peter Cock.
# All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.
"""Cross checking our SAM/BAM support against pysam."""

try:
    import pysam
except ImportError:
    from Bio import MissingPythonDependencyError
    raise MissingPythonDependencyError(
        "Install pysam if you want to test against it.")

import unittest
from itertools import izip_longest

from Bio.Sequencing.SamBam import SamIterator, BamIterator

class CrossCheckParsing(unittest.TestCase):
    """Cross checking our SAM/BAM parsing against pysam."""

    def compare(self, a_iter, b_iter):
        self.assertEqual(a_iter.nreferences, b_iter.nreferences)
        self.assertEqual(a_iter.references, b_iter.references)
        self.assertEqual(a_iter.lengths, b_iter.lengths)
        if a_iter.header and b_iter.header:
            #pysam doesn't infer a minimal SAM header from BAM header
            self.assertEqual(a_iter.header, b_iter.header)
        for a, b in izip_longest(a_iter, b_iter):
            self.assertTrue(b is not None, "Extra read in a: %r" % str(a))
            self.assertTrue(a is not None, "Extra read in b: %r" % str(b))
            self.assertEqual(a.qname, b.qname)
            self.assertEqual(a.flag, b.flag)
            #See http://code.google.com/p/pysam/issues/detail?id=25
            #self.assertEqual(a.rname, b.rname)
            self.assertEqual(a.pos, b.pos)
            self.assertEqual(a.alen, b.alen)
            self.assertEqual(a.aend, b.aend)
            self.assertEqual(a.mapq, b.mapq)
            self.assertEqual(a.cigar, b.cigar)
            #See http://code.google.com/p/pysam/issues/detail?id=25
            #self.assertEqual(a.mrnm, b.mrnm)
            self.assertEqual(a.mpos, b.mpos)
            self.assertEqual(a.isize, b.isize) #legacy alias
            self.assertEqual(a.seq, b.seq)
            self.assertEqual(a.qual, b.qual)
            #TODO - tags (not represented same way at the moment)

            #assert str(a) == str(b), "Reads disagree,\n%s\n%s\n" % (a,b)
            #Would compare str(a)==str(b) but pysam does not attempt
            #to return a valid SAM record like this.
            #See http://code.google.com/p/pysam/issues/detail?id=74
            #and http://code.google.com/p/pysam/issues/detail?id=75
    
    #TODO, use pysam on the SAM file
    #http://code.google.com/p/pysam/issues/detail?id=73
    #compare(SamIterator(open("SamBam/ex1.sam")),
    #        pysam.Samfile("SamBam/ex1.sam", "r"))
    #Avoid this by using a copy of the SAM file with a header:

    def test_ex1_header_sam_vs_sam(self):
        self.compare(SamIterator(open("SamBam/ex1_header.sam")),
                     pysam.Samfile("SamBam/ex1_header.sam", "r"))

    def test_ex1_header_sam_vs_bam(self):
        self.compare(SamIterator(open("SamBam/ex1_header.sam")),
                     pysam.Samfile("SamBam/ex1_header.bam", "rb"))

    def test_ex1_header_bam_vs_bam(self):
        self.compare(BamIterator(open("SamBam/ex1_header.bam", "rb")),
                     pysam.Samfile("SamBam/ex1_header.bam", "rb"))

    #pysam:
    #ValueError: file header is empty (mode='r') - is it SAM/BAM format?
    #def test_ex1_bam_vs_bam(self):
    #    self.compare(BamIterator(open("SamBam/ex1.bam", "rb")),
    #                 pysam.Samfile("SamBam/ex1.bam", "rb"))
    #
    #def test_ex1_sam_vs_sam(self):
    #    self.compare(SamIterator(open("SamBam/ex1.sam")),
    #                 pysam.Samfile("SamBam/ex1.sam", "r"))


class CrossCheckRandomAccess(unittest.TestCase):
    """Cross checking our BAM random access against pysam."""

    def index_check(self, bam, bai, regions):
        print bam
        pysam_bam = pysam.Samfile(bam, "rb")
        handle = open(bam, "rb")
        biopy_bam = BamIterator(handle, bai_filename = bai)
        for ref, start, end in regions:
            print "%s region %i:%i" % (ref, start, end)
            pysam_list = list(pysam_bam.fetch(ref, start, end))
            print "%s region %i:%i has %i reads (pysam)" \
                  % (ref, start, end, len(pysam_list))
            if len(pysam_list) <= 10:
                for read in pysam_list:
                    print " - %s at %i" % (read.qname, read.pos)
            else:
                for read in pysam_list[:5]:
                    print " - %s at %i" % (read.qname, read.pos)
                print " - etc"
                for read in pysam_list[-5:]:
                    print " - %s at %i" % (read.qname, read.pos)
            biopy_list = list(biopy_bam.fetch(ref, start, end))
            print "%s region %i:%i has %i reads (biopy)" \
                  % (ref, start, end, len(biopy_list))
            if len(biopy_list) <= 10:
                for read in biopy_list:
                    print " - %s at %i" % (read.qname, read.pos)
            else:
                for read in biopy_list[:5]:
                    print " - %s at %i" % (read.qname, read.pos)
                print " - etc"
                for read in biopy_list[-5:]:
                    print " - %s at %i" % (read.qname, read.pos)
            #assert len(pysam_list) == len(biopy_list), \
            print "%i vs %i reads for %s region %i:%i" \
                % (len(pysam_list), len(biopy_list), ref, start, end)
        handle.close()

    def test_index_ex1(self):
        self.index_check("SamBam/ex1.bam", "SamBam/ex1.bam.bai", [
                            ("chr1", 120, 130),
                        ])

    def test_index_bins(self):
        self.index_check("SamBam/bins.bam", "SamBam/bins.bam.bai", [
                            ("large", 120, 130),
                            ("large", 1000, 1010),
                        ])


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
