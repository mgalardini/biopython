# Copyright 2011 by Peter Cock.  All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.
#
"""Sequence search input/output.

The idea of this module (like those in BioPerl) is that while SeqIO is for
(annotated) sequences, and AlignIO is for multiple sequence alignments, here
we are interested in searching one or more query sequences against a database
of other sequences. Any query sequence will have zero or more matches, and
for each match there may be more than one hit (or HSP), each with a score and
typically a pairwise sequence alignment between the query and match sequence.

Input
=====
The main function is Bio.SearchIO.parse(...) which takes an input file handle
or filename, and format string. This returns an iterator giving search results
for each query sequence:

    >>> from Bio import SearchIO
    >>> for search in SearchIO.parse("Blast/xbt010.xml", "blast-xml"):
    ...     print search.query_id, len(search)
    gi|3298468|dbj|BAA31520.1| 10
    gi|2781234|pdb|1JLY|B 10
    gi|4959044|gb|AAD34209.1|AF069992_1 10
    gi|671626|emb|CAA85685.1| 10

If you know the file has results for only one query sequence, you won't want
an iterator - use the read function instead (following the convention used in
Bio.SeqIO and Bio.AlignIO etc):

    >>> from Bio import SearchIO
    >>> search = SearchIO.read("Blast/xbt001.xml", "blast-xml")
    >>> print search.query_id, len(search)
    gi|49176427|ref|NP_418280.3| 212

Each query sequence may give more the one match sequence, and furthermore each
match may have more than one hit (pairwise alignment, HSP). Here we'll look at
a BLAST pairwise alignment plain text file for a single query:

    >>> from Bio import SearchIO
    >>> search = SearchIO.read("Blast/bt057.txt", "blast-text")
    >>> print "Query %s has %i matches" % (search.query_id, len(search))
    Query gi|585505|sp|Q08386|MOPB_RHOCA has 13 matches
    >>> for match in search:
    ...     print "Match %s has %i hits" % (match.match_id, len(match))
    Match gi|585505|sp|Q08386|MOPB_RHOCA has 1 hits
    Match gi|585504|sp|Q08385|MOPA_RHOCA has 1 hits
    Match gi|585492|sp|P37733|MODA_AZOVI has 2 hits
    Match gi|1709070|sp|P46930|MODE_ECOLI has 1 hits
    Match gi|1709071|sp|P45324|MODE_HAEIN has 1 hits
    Match gi|585502|sp|P04952|MOP1_CLOPA has 2 hits
    Match gi|127241|sp|P08854|MOP2_CLOPA has 2 hits
    Match gi|585503|sp|P38366|MOP3_CLOPA has 2 hits
    Match gi|1170996|sp|P45183|MOP_HAEIN has 1 hits
    Match gi|1709069|sp|P09833|MODC_ECOLI has 1 hits
    Match gi|585500|sp|P37732|MODD_AZOVI has 1 hits
    Match gi|2507168|sp|P08838|PT1_BACSU has 1 hits
    Match gi|729786|sp|Q05355|HYDL_STRHA has 1 hits

For some file formats, like BLAST XML and the pairwise plain text, you get the
aligned sequences for each hit:

    >>> for hit in match: print hit
    SingleLetterAlphabet() alignment with 2 rows and 62 columns
    AIEAGVAKLLSSFEKSLNLDPAEVLRGLSLRTSARNAWACKVWS...EGQ gi|585505|sp|Q08386|MOPB_RHOCA
    AVELGGEIRFSTELQSFEQDPAGVTAVIKSRRSGEHTTVRADYL...IGQ gi|729786|sp|Q05355|HYDL_STRHA

For other file formats, like the standard 12 column BLAST tabular output, the
aligned sequences are not given.
     
If you need random access to the search results by query ID, use the index
function which returns a read-only dictionary like object (following the
convention used in Bio.SeqIO):

    >>> from Bio import SearchIO
    >>> searches = SearchIO.index("Blast/xbt010.xml", "blast-xml")
    >>> len(searches)
    4
    >>> print len(searches["gi|2781234|pdb|1JLY|B"])
    10


File Formats
============
When specifying the file format, use lowercase strings:

 - blast-stdtab - NCBI BLAST standard 12 column tabular
 - blast-text   - NCBI BLAST pairwise text (obsolete)
 - blast-xml    - NCBI BLAST XML
 - fasta-m10    - For the pairswise alignments output by Bill Pearson's FASTA
                  tools when used with the -m 10 command line option for machine
                  readable output.

Note that while Bio.SearchIO will read all the above file formats, it cannot
yet write to any of them.

Bio.AlignIO supports parsing some of the same format names (e.g. fasta-m10)
giving access to the pairwise alignments only (ignoring queries with no hits).
"""
from _objects import SearchResult, TopMatches, HSP
import FastaIO
import BlastIO

"""Note to developers: Low level iterators

I want to be able to use the same parsers for pairwise alignments in both
Bio.AlignIO (HSPs only) and Bio.SearchIO (including negative results). Also,
for any one query there could be 100s of matches - which means a rather large
query result object for SearchIO, but for AlignIO we can iterate over these
without having to load them all into memory. Therefore, my plan is...

Each low level iterator will return HSP objects, or for queries with no
matches just the query name (string).

So, for AlignIO, we just loop over the iterator, and return any objects which
are pairwise alignments (HSPAlignment is both HSP and MultipleSeqAlignment),
and ignore plain HSP objects (no pairwise alignment) or strings (no hits).
For SearchIO, we loop over the iterator, batching by query_id. Although this
batching code is non-trivial, it only needs to be done here at the top level,
and not repeated in each individual parser.

TODO - We can cope with getting a string of the query_id at the start of each
new query, but is this a good idea? Should decided one way or the other and
enforce it.
"""
_FormatToIterator = {
                     "blast-xml" : BlastIO.BlastXmlIterator,
                     "blast-text" : BlastIO.BlastPairwiseTextIterator,
                     "blast-stdtab" : BlastIO.BlastStandardTabularIterator,
                     "fasta-m10" : FastaIO.FastaM10Iterator,
                     }

def parse(handle, format):
    """Parse a file containing a search results.

     - handle   - handle to the file, or the filename as a string.
     - format   - string describing the file format.

    For example, parsing a BLAST XML file:

    >>> from Bio import SearchIO
    >>> for search in SearchIO.parse("Blast/xbt010.xml", "blast-xml"):
    ...     print "Query", search.query_id, "matches", len(search)
    Query gi|3298468|dbj|BAA31520.1| matches 10
    Query gi|2781234|pdb|1JLY|B matches 10
    Query gi|4959044|gb|AAD34209.1|AF069992_1 matches 10
    Query gi|671626|emb|CAA85685.1| matches 10

    Or, parsing an obsolete BLAST pairwise text file:

    >>> from Bio import SearchIO
    >>> for search in SearchIO.parse("Blast/bt078.txt", "blast-text"):
    ...     print "Query", search.query_id, "matches", len(search)
    ...     for match in search: print match
    Query gi|6273291|gb|AF191665.1|AF191665 matches 0
    Query gi|6273290|gb|AF191664.1|AF191664 matches 0
    Query gi|6273289|gb|AF191663.1|AF191663 matches 0
    Query gi|6273287|gb|AF191661.1|AF191661 matches 2
    dbj|BAE48041.1|
    emb|CAJ32483.1|
    Query gi|6273286|gb|AF191660.1|AF191660 matches 0
    Query gi|6273285|gb|AF191659.1|AF191659 matches 0
    Query gi|6273284|gb|AF191658.1|AF191658 matches 0

    Or, parsing a FASTA -m 10 file:

    >>> from Bio import SearchIO
    >>> for search in SearchIO.parse("Fasta/output003.m10", "fasta-m10"):
    ...     print "Query", search.query_id, "matches", len(search)
    ...     for match in search: print match
    Query gi|152973837|ref|YP_001338874.1| matches 1
    gi|10955263|ref|NP_052604.1|
    Query gi|152973838|ref|YP_001338875.1| matches 0
    Query gi|152973839|ref|YP_001338876.1| matches 0
    Query gi|152973840|ref|YP_001338877.1| matches 1
    gi|10955265|ref|NP_052606.1|
    Query gi|152973841|ref|YP_001338878.1| matches 1
    gi|10955264|ref|NP_052605.1|

    If however your file has one and only one result (i.e. there was just a
    single search query), use the Bio.SearchIO.read(handle, format) function
    instead.
    """
    handle_close = False

    if isinstance(handle, basestring):
        handle = open(handle, "rU")
        #TODO - On Python 2.5+ use with statement to close handle
        handle_close = True

    #Try and give helpful error messages:
    if not isinstance(format, basestring):
        raise TypeError("Need a string for the file format (lower case)")
    if not format:
        raise ValueError("Format required (lower case string)")
    if format != format.lower():
        raise ValueError("Format string '%s' should be lower case" % format)

    #Map the file format to a sequence iterator:
    if format in _FormatToIterator:
        i = _FormatToIterator[format](handle)
    else:
        raise ValueError("Unknown format '%s'" % format)

    result = None
    for a in i:
        if isinstance(a, basestring):
            #Query with no hits
            if result is not None:
                #Also means end of the previous query
                yield result
            result = SearchResult(a, [])
        elif result is None:
            #New query, cache it and see if it has more hits...
            result = SearchResult(a.query_id,
                                  [TopMatches(a.query_id, a.match_id, [a])])
        elif result.query_id == a.query_id:
            #Combine this as it is for the same query
            if a.match_id == result[-1].match_id:
                result[-1].append(a)
            else:
                result.append(TopMatches(a.query_id, a.match_id, [a]))
        else:
            #New query, so old query is finished now
            yield result
            #Cache new query and see if it has more hits...
            result = SearchResult(a.query_id,
                                  [TopMatches(a.query_id, a.match_id, [a])])
    if result is not None:
        yield result
    if handle_close:
        handle.close()


def read(handle, format):
    """Parse a file containing a single search result.

     - handle   - handle to the file, or the filename as a string.
     - format   - string describing the file format.

    This function is for use parsing search result files containing
    exactly one record.  For example, reading a BLAST XML file:

    >>> from Bio import SearchIO
    >>> search = SearchIO.read("Blast/xbt001.xml", "blast-xml")
    >>> print "Query", search.query_id
    Query gi|49176427|ref|NP_418280.3|
    >>> print "Has matches to %i database entries" % len(search)
    Has matches to 212 database entries

    If the handle contains no results, or more than one result,
    an exception is raised.  For example:

    >>> from Bio import SearchIO
    >>> search = SearchIO.read("Blast/xbt010.xml", "blast-xml")
    Traceback (most recent call last):
        ...
    ValueError: More than one result found in handle

    If however you want the first result from a file containing multiple
    results this function would raise an exception (as shown in the
    example above).  Instead use:

    >>> from Bio import SearchIO
    >>> search = SearchIO.parse("Blast/xbt010.xml", "blast-xml").next()
    >>> print "First query's ID", search.query_id, "matches", len(search)
    First query's ID gi|3298468|dbj|BAA31520.1| matches 10
    >>> for match in search: print match
    gi|3298468|dbj|BAA31520.1|
    gi|227434194|gb|ACP28878.1|
    gi|223541319|gb|EEF42870.1|
    gi|225441155|ref|XP_002267788.1|
    gi|209892837|gb|ACI95283.1|
    gi|21284370|gb|AAB51393.2|
    gi|22858917|gb|AAN05780.1|
    gi|21284372|gb|AAB51394.2|
    gi|38198150|emb|CAE53881.1|
    gi|162809290|dbj|BAF95576.1|

    Use the Bio.SearchIO.parse(handle, format) function if you want to read
    multiple results from the handle.
    """
    iterator = parse(handle, format)
    try:
        first = iterator.next()
    except StopIteration:
        first = None
    if first is None:
        raise ValueError("No results found in handle")
    try:
        second = iterator.next()
    except StopIteration:
        second = None
    if second is not None:
        raise ValueError("More than one result found in handle")
    return first

def index(filename, format):
    """Random access to search results.

    e.g. Using BLAST XML,

    >>> from Bio import SearchIO
    >>> searches = SearchIO.index("Blast/xbt010.xml", "blast-xml")
    >>> len(searches)
    4
    >>> print len(searches["gi|2781234|pdb|1JLY|B"])
    10

    Or using the obsolete BLAST pairwise plain text,

    >>> from Bio import SearchIO
    >>> searches = SearchIO.index("Blast/bt081.txt", "blast-text")
    >>> len(searches)
    7
    >>> print len(searches["gi|5052071|gb|AF067555.1|AF067555"])
    1

    """
    #Quick in memory implementation to make doctests pass
    #See the Bio.SeqIO module for what I have in mind here.
    answer = dict()
    for search in parse(filename, format):
        if search.query_id in answer:
            raise KeyError(search.query_id)
        else:
            answer[search.query_id] = search
    return answer

def _test():
    """Run the Bio.SearchIO module's doctests (PRIVATE).

    This will try and locate the unit tests directory, and run the doctests
    from there in order that the relative paths used in the examples work.
    """
    import doctest
    import os
    if os.path.isdir(os.path.join("..","..","Tests")):
        print "Runing doctests..."
        cur_dir = os.path.abspath(os.curdir)
        os.chdir(os.path.join("..","..","Tests"))
        doctest.testmod()
        os.chdir(cur_dir)
        del cur_dir
        print "Done"
    elif os.path.isdir(os.path.join("Tests")):
        print "Runing doctests..."
        cur_dir = os.path.abspath(os.curdir)
        os.chdir(os.path.join("Tests"))
        doctest.testmod()
        os.chdir(cur_dir)
        del cur_dir
        print "Done"

if __name__ == "__main__":
    _test()

