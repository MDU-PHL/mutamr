import argparse, sys, pathlib, tempfile
from distutils.command.install_egg_info import to_filename
from .Fastq2vcf import Fastq2Vcf



"""
mutAMR is designed to be a very simple lightweigth tool to identify variants from genomic data. 

"""

def run(args):
    
    
    
    V = Fastq2Vcf(read1 = args.read1,
                read2= args.read2,
                threads=args.threads,
                ram = args.ram,
                seq_id= args.seq_id,
                reference = args.reference,
                keep = args.keep,
                mtb = args.mtb,
                mindepth = args.min_depth,
                minfrac = args.min_frac,
                force = args.force,
                tmp = args.tmp)
    V.run()


def search_catalog(args):
    pass

def set_parsers():
    parser = argparse.ArgumentParser(
        description="Easy variant detection for AMR - developed for use in public health", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    
    subparsers = parser.add_subparsers(help="Types of detection")
    
    parser_sub_wgs = subparsers.add_parser('wgs', help='Generate vcf for identification of variants from WGS data TB.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser_sub_wgs.add_argument(
        "--read1",
        "-1",
        help="path to read1",
        default = ""
    )
    parser_sub_wgs.add_argument(
        "--read2",
        "-2",
        help="path to read2",
        default = ""
    )
    parser_sub_wgs.add_argument(
        "--seq_id",
        "-s",
        help="Sequence name",
        default = "mutamr"
    )
    parser_sub_wgs.add_argument(
        "--reference",
        "-r",
        help="Reference to use for alignment. Not required if using --mtb",
        default = ""
    )
    parser_sub_wgs.add_argument(
        "--annotation_species",
        "-a",
        help="Name of species for annotation - needs to be a snpEff annotation config. Not required if using --mtb",
        default = ""
    )
    parser_sub_wgs.add_argument(
        '--min_depth',
        '-md',
        help= f"Minimum depth to call a variant",
        default= 20
    )
    parser_sub_wgs.add_argument(
        '--min_frac',
        '-mf',
        help= f"Minimum proportion to call a variant (0-1)",
        default= 0.1
    )

    parser_sub_wgs.add_argument(
        '--threads',
        '-t',
        help = "Threads to use for generation of vcf file.",
        default = 8
    )
    parser_sub_wgs.add_argument(
        '--ram',
        help = "Max ram to use",
        default = 8
    )
    parser_sub_wgs.add_argument(
        '--tmp',
        help = "temp directory to use",
        default = f"{pathlib.Path(tempfile.gettempdir())}"
    )
    parser_sub_wgs.add_argument(
        '--mtb',
        help = "Run for Mtb",
        action = "store_true"
    )
    parser_sub_wgs.add_argument(
        '--keep',
        '-k',
        help = "Keep accessory files for further use.",
        action = "store_true"
    )
    parser_sub_wgs.add_argument(
        '--force',
        '-f',
        help = "Force override an existing mutamr run.",
        action = "store_true"
    )

    
    parser_sub_wgs.set_defaults(func=run)
    args = parser.parse_args(args=None if sys.argv[1:]  else ['--help'])
    return args

 
def main():
    """
    run pipeline
    """

    args = set_parsers()
    args.func(args)
    

if __name__ == "__main__":
    main()
