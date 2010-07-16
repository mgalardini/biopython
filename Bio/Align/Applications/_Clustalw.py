# Copyright 2009 by Cymon J. Cox.  All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.
"""Command line wrapper for the multiple alignment program Clustal W.

http://www.clustal.org/

Citation:

Larkin MA, Blackshields G, Brown NP, Chenna R, McGettigan PA, McWilliam H, 
Valentin F, Wallace IM, Wilm A, Lopez R, Thompson JD, Gibson TJ, Higgins DG.
(2007). Clustal W and Clustal X version 2.0. Bioinformatics, 23, 2947-2948. 

Last checked against versions: 1.83 and 2.0.10
"""
import os
import types
from Bio.Application import _Option, _Switch, AbstractCommandline

class ClustalwCommandline(AbstractCommandline):
    """Command line wrapper for clustalw (version one or two)."""
    #TODO - Should we default to cmd="clustalw2" now?
    def __init__(self, cmd="clustalw", **kwargs):
        self.parameters = \
            [
            _Option(["-infile", "-INFILE", "INFILE", "infile"],
                    ["input", "file"],
                    None,
                    False,
                    "Input sequences.",
                    True),
            _Option(["-profile1", "-PROFILE1", "PROFILE1", "profile1"],
                    ["input", "file"],
                    None,
                    False,
                    "Profiles (old alignment).",
                    True),
            _Option(["-profile2", "-PROFILE2", "PROFILE2", "profile2"],
                    ["input", "file"],
                    None,
                    False,
                    "Profiles (old alignment).",
                    True),
            ################## VERBS (do things) #############################
            _Switch(["-options", "-OPTIONS", "OPTIONS", "options"],
                    ["input"],
                    "List the command line parameters"),
            _Switch(["-help", "-HELP", "HELP", "help"],
                    ["input"],
                    "Outline the command line params."),
            _Switch(["-check", "-CHECK", "CHECK", "check"],
                    ["input"],
                    "Outline the command line params."),
            _Switch(["-fullhelp", "-FULLHELP", "FULLHELP", "fullhelp"],
                    ["input"],
                    "Output full help content."),
            _Switch(["-align", "-ALIGN", "ALIGN", "align"],
                    ["input"],
                    "Do full multiple alignment."),
            _Switch(["-tree", "-TREE", "TREE", "tree"],
                    ["input"],
                    "Calculate NJ tree."),
            _Option(["-bootstrap", "-BOOTSTRAP", "BOOTSTRAP", "bootstrap"],
                    ["input"],
                    lambda x: isinstance(x, int),
                    False,
                    "Bootstrap a NJ tree (n= number of bootstraps; def. = 1000).",
                    True),
            _Switch(["-convert", "-CONVERT", "CONVERT", "convert"],
                    ["input"],
                    "Output the input sequences in a different file format."),
            ##################### PARAMETERS (set things) #########################
            # ***General settings:****
            # Makes no sense in biopython
            #_Option(["-interactive", "-INTERACTIVE", "INTERACTIVE", "interactive"],
            #        ["input"],
            #        lambda x: 0, #Does not take value
            #        False,
            #        "read command line, then enter normal interactive menus",
            #        False),
            _Switch(["-quicktree", "-QUICKTREE", "QUICKTREE", "quicktree"],
                    ["input"],
                    "Use FAST algorithm for the alignment guide tree"),
            _Option(["-type", "-TYPE", "TYPE", "type"],
                    ["input"],
                    lambda x: x in ["PROTEIN", "DNA", "protein", "dna"],
                    False,
                    "PROTEIN or DNA sequences",
                    True),
            _Switch(["-negative", "-NEGATIVE", "NEGATIVE", "negative"],
                    ["input"],
                    "Protein alignment with negative values in matrix"),
            _Option(["-outfile", "-OUTFILE", "OUTFILE", "outfile"],
                    ["input", "file"],
                    None,
                    False,
                    "Output sequence alignment file name",
                    True),
            _Option(["-output", "-OUTPUT", "OUTPUT", "output"],
                    ["input"],
                    lambda x: x in ["GCG", "GDE", "PHYLIP", "PIR", "NEXUS",
                                    "gcg", "gde", "phylip", "pir", "nexus"],
                    False,
                    "Output format: GCG, GDE, PHYLIP, PIR or NEXUS",
                    True),
            _Option(["-outorder", "-OUTORDER", "OUTORDER", "outorder"],
                    ["input"],
                    lambda x: x in ["INPUT", "input", "ALIGNED", "aligned"],
                    False,
                    "Output taxon order: INPUT or ALIGNED",
                    True),
            _Option(["-case", "-CASE", "CASE", "case"],
                    ["input"],
                    lambda x: x in ["UPPER", "upper", "LOWER", "lower"],
                    False,
                    "LOWER or UPPER (for GDE output only)",
                    True),
            _Option(["-seqnos", "-SEQNOS", "SEQNOS", "seqnos"],
                    ["input"],
                    lambda x: x in ["ON", "on", "OFF", "off"],
                    False,
                    "OFF or ON (for Clustal output only)",
                    True),
            _Option(["-seqno_range", "-SEQNO_RANGE", "SEQNO_RANGE", "seqno_range"],
                    ["input"],
                    lambda x: x in ["ON", "on", "OFF", "off"],
                    False,
                    "OFF or ON (NEW- for all output formats)",
                    True),
            _Option(["-range", "-RANGE", "RANGE", "range"],
                    ["input"],
                    None,
                    False,
                    "Sequence range to write starting m to m+n. " + \
                    "Input as string eg. '24,200'",
                    True),
            _Option(["-maxseqlen", "-MAXSEQLEN", "MAXSEQLEN", "maxseqlen"],
                    ["input"],
                    lambda x: isinstance(x, int),
                    False,
                    "Maximum allowed input sequence length",
                    True),
            _Switch(["-quiet", "-QUIET", "QUIET", "quiet"],
                    ["input"],
                    "Reduce console output to minimum"),
            _Switch(["-stats", "-STATS", "STATS", "stats"],
                    ["input"],
                    "Log some alignents statistics to file"),
            # ***Fast Pairwise Alignments:***
            _Option(["-ktuple", "-KTUPLE", "KTUPLE", "ktuple"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Word size",
                    True),
            _Option(["-topdiags", "-TOPDIAGS", "TOPDIAGS", "topdiags"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Number of best diags.",
                    True),
            _Option(["-window", "-WINDOW", "WINDOW", "window"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Window around best diags.",
                    True),
            _Option(["-pairgap", "-PAIRGAP", "PAIRGAP", "pairgap"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Gap penalty",
                    True),
            _Option(["-score", "-SCORE", "SCORE", "score"],
                    ["input"],
                    lambda x: x in ["percent", "PERCENT", "absolute",
                                    "ABSOLUTE"],
                    False,
                    "Either: PERCENT or ABSOLUTE",
                    True),
            # ***Slow Pairwise Alignments:***
            _Option(["-pwmatrix", "-PWMATRIX", "PWMATRIX", "pwmatrix"],
                    ["input"],
                    lambda x: x in ["BLOSUM", "PAM", "GONNET", "ID", \
                                    "blosum", "pam", "gonnet", "id"] or \
                                    os.path.exists(x),
                    False,
                    "Protein weight matrix=BLOSUM, PAM, GONNET, ID or filename",
                    True),
            _Option(["-pwdnamatrix", "-PWDNAMATRIX", "PWDNAMATRIX", "pwdnamatrix"],
                    ["input"],
                    lambda x: x in ["IUB", "CLUSTALW", "iub", "clustalw"] or \
                                    os.path.exists(x),
                    False,
                    "DNA weight matrix=IUB, CLUSTALW or filename",
                    True),
            _Option(["-pwgapopen", "-PWGAPOPEN", "PWGAPOPEN", "pwgapopen"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Gap opening penalty",
                    True),
            _Option(["-pwgapext", "-PWGAPEXT", "PWGAPEXT", "pwgapext"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Gap opening penalty",
                    True),
            # ***Multiple Alignments:***
            _Option(["-newtree", "-NEWTREE", "NEWTREE", "newtree"],
                    ["output", "file"],
                    None,
                    False,
                    "Output file name for newly created guide tree",
                    True),
            _Option(["-usetree", "-USETREE", "USETREE", "usetree"],
                    ["input", "file"],
                    lambda x: os.path.exists,
                    False,
                    "File name of guide tree",
                    True),
            _Option(["-matrix", "-MATRIX", "MATRIX", "matrix"],
                    ["input"],
                    lambda x: x in ["BLOSUM", "PAM", "GONNET", "ID", \
                                    "blosum", "pam", "gonnet", "id"] or \
                                    os.path.exists(x),
                    False,
                    "Protein weight matrix=BLOSUM, PAM, GONNET, ID or filename",
                    True),
            _Option(["-dnamatrix", "-DNAMATRIX", "DNAMATRIX", "dnamatrix"],
                    ["input"],
                    lambda x: x in ["IUB", "CLUSTALW", "iub", "clustalw"] or \
                                    os.path.exists(x),
                    False,
                    "DNA weight matrix=IUB, CLUSTALW or filename",
                    True),
            _Option(["-gapopen", "-GAPOPEN", "GAPOPEN", "gapopen"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Gap opening penalty",
                    True),
            _Option(["-gapext", "-GAPEXT", "GAPEXT", "gapext"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Gap extension penalty",
                    True),
            _Switch(["-endgaps", "-ENDGAPS", "ENDGAPS", "endgaps"],
                    ["input"],
                    "No end gap separation pen."),
            _Option(["-gapdist", "-GAPDIST", "GAPDIST", "gapdist"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Gap separation pen. range",
                    False),
            _Switch(["-nopgap", "-NOPGAP", "NOPGAP", "nopgap"],
                    ["input"],
                    "Residue-specific gaps off"),
            _Switch(["-nohgap", "-NOHGAP", "NOHGAP", "nohgap"],
                    ["input"],
                    "Hydrophilic gaps off"),
            _Switch(["-hgapresidues", "-HGAPRESIDUES", "HGAPRESIDUES", "hgapresidues"],
                    ["input"],
                    "List hydrophilic res."),
            _Option(["-maxdiv", "-MAXDIV", "MAXDIV", "maxdiv"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "% ident. for delay",
                    True),
            _Option(["-transweight", "-TRANSWEIGHT", "TRANSWEIGHT", "transweight"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Transitions weighting",
                    True),
            _Option(["-iteration", "-ITERATION", "ITERATION", "iteration"],
                    ["input"],
                    lambda x: x in ["NONE", "TREE", "ALIGNMENT",
                                    "none", "tree", "alignment"],
                    False,
                    "NONE or TREE or ALIGNMENT",
                    True),
            _Option(["-numiter", "-NUMITER", "NUMITER", "numiter"],
                    ["input"],
                    lambda x:  isinstance(x, int),
                    False,
                    "maximum number of iterations to perform",
                    False),
            _Switch(["-noweights", "-NOWEIGHTS", "NOWEIGHTS", "noweights"],
                    ["input"],
                    "Disable sequence weighting"),
            # ***Profile Alignments:***
            _Switch(["-profile", "-PROFILE", "PROFILE", "profile"],
                    ["input"],
                    "Merge two alignments by profile alignment"),
            _Option(["-newtree1", "-NEWTREE1", "NEWTREE1", "newtree1"],
                    ["output", "file"],
                    None,
                    False,
                    "Output file name for new guide tree of profile1",
                    True),
            _Option(["-newtree2", "-NEWTREE2", "NEWTREE2", "newtree2"],
                    ["output", "file"],
                    None,
                    False,
                    "Output file for new guide tree of profile2",
                    True),
            _Option(["-usetree1", "-USETREE1", "USETREE1", "usetree1"],
                    ["input", "file"],
                    lambda x: os.path.exists,
                    False,
                    "File name of guide tree for profile1",
                    True),
            _Option(["-usetree2", "-USETREE2", "USETREE2", "usetree2"],
                    ["input", "file"],
                    lambda x: os.path.exists,
                    False,
                    "File name of guide tree for profile2",
                    True),
            # ***Sequence to Profile Alignments:***
            _Switch(["-sequences", "-SEQUENCES", "SEQUENCES", "sequences"],
                    ["input"],
                    "Sequentially add profile2 sequences to profile1 alignment"),
            _Switch(["-nosecstr1", "-NOSECSTR1", "NOSECSTR1", "nosecstr1"],
                    ["input"],
                    "Do not use secondary structure-gap penalty mask for profile 1"),
            _Switch(["-nosecstr2", "-NOSECSTR2", "NOSECSTR2", "nosecstr2"],
                    ["input"],
                    "Do not use secondary structure-gap penalty mask for profile 2"),
            # ***Structure Alignments:***
            _Option(["-secstrout", "-SECSTROUT", "SECSTROUT", "secstrout"],
                    ["input"],
                    lambda x: x in ["STRUCTURE", "MASK", "BOTH", "NONE",
                                    "structure", "mask", "both", "none"],
                    False,
                    "STRUCTURE or MASK or BOTH or NONE output in alignment file",
                    True),
            _Option(["-helixgap", "-HELIXGAP", "HELIXGAP", "helixgap"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Gap penalty for helix core residues",
                    True),
            _Option(["-strandgap", "-STRANDGAP", "STRANDGAP", "strandgap"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "gap penalty for strand core residues",
                    True),
            _Option(["-loopgap", "-LOOPGAP", "LOOPGAP", "loopgap"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Gap penalty for loop regions",
                    True),
            _Option(["-terminalgap", "-TERMINALGAP", "TERMINALGAP", "terminalgap"],
                    ["input"],
                    lambda x: isinstance(x, int) or \
                              isinstance(x, float),
                    False,
                    "Gap penalty for structure termini",
                    True),
            _Option(["-helixendin", "-HELIXENDIN", "HELIXENDIN", "helixendin"],
                    ["input"],
                    lambda x: isinstance(x, int),
                    False,
                    "Number of residues inside helix to be treated as terminal",
                    True),
            _Option(["-helixendout", "-HELIXENDOUT", "HELIXENDOUT", "helixendout"],
                    ["input"],
                    lambda x: isinstance(x, int),
                    False,
                    "Number of residues outside helix to be treated as terminal",
                    True),
            _Option(["-strandendin", "-STRANDENDIN", "STRANDENDIN", "strandendin"],
                    ["input"],
                    lambda x: isinstance(x, int),
                    False,
                    "Number of residues inside strand to be treated as terminal",
                    True),
            _Option(["-strandendout", "-STRANDENDOUT", "STRANDENDOUT", "strandendout"],
                    ["input"],
                    lambda x: isinstance(x, int),
                    False,
                    "number of residues outside strand to be treated as terminal",
                    True),
            # ***Trees:***
            _Option(["-outputtree", "-OUTPUTTREE", "OUTPUTTREE", "outputtree"],
                    ["input"],
                    lambda x: x in ["NJ", "PHYLIP", "DIST", "NEXUS",
                                    "nj", "phylip", "dist", "nexus"],
                    False,
                    "nj OR phylip OR dist OR nexus",
                    True),
            _Option(["-seed", "-SEED", "SEED", "seed"],
                    ["input"],
                    lambda x: isinstance(x, int),
                    False,
                    "Seed number for bootstraps.",
                    True),
            _Switch(["-kimura", "-KIMURA", "KIMURA", "kimura"],
                    ["input"],
                    "Use Kimura's correction."),
            _Switch(["-tossgaps", "-TOSSGAPS", "TOSSGAPS", "tossgaps"],
                    ["input"],
                    "Ignore positions with gaps."),
            _Option(["-bootlabels", "-BOOTLABELS", "BOOTLABELS", "bootlabels"],
                    ["input"],
                    lambda x: x in ["NODE", "BRANCH", "node", "branch"],
                    False,
                    "Node OR branch position of bootstrap values in tree display",
                    True),
            _Option(["-clustering", "-CLUSTERING", "CLUSTERING", "clustering"],
                    ["input"],
                    lambda x: x in ["NJ", "UPGMA", "nj", "upgma"],
                    False,
                    "NJ or UPGMA",
                    True)
            ]
        AbstractCommandline.__init__(self, cmd, **kwargs)
