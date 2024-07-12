import argparse, sys, pathlib
from distutils.command.install_egg_info import to_filename

"""
mutAMR is designed to be a very simple lightweigth tool to identify variants from genomic data. 

"""

def run(args):
    pass

def search_catalog(args):
    pass

def set_parsers():
    parser = argparse.ArgumentParser(
        description="Easy variant detection for AMR - developed for use in public health", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    
    subparsers = parser.add_subparsers(help="Types of detection")
    
    parser_sub_tb = subparsers.add_parser('tb', help='Generate vcf for identification of variants from WGS data TB.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser_sub_tb.add_argument(
        "--read1",
        "-1",
        help="path to read1",
        default = ""
    )
    parser_sub_tb.add_argument(
        "--read2",
        "-2",
        help="path to read2",
        default = ""
    )
    parser_sub_tb.add_argument(
        "--seq_id",
        "-s",
        help="Sequence name",
        default = ""
    )
    parser_sub_tb.add_argument(
        '--min_depth',
        '-m',
        help= f"Minimum depth to call a variant",
        default= 20
    )
    parser_sub_tb.add_argument(
        '--threads',
        '-t',
        help = "Threads to use for generation of vcf file.",
        default = 8
    )
    parser_sub_tb.add_argument(
        '--keep_bam',
        '-k',
        help = "Keep bam files for further use.",
        action = "store_true"
    )
    
    

    # parser_sub_search = subparsers.add_parser('search', help='Search the provided catalog for variant information', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # parser_sub_search.add_argument(
    #     "--catalog",
    #     "-c",
    #     help="csv variant catalog",
    #     # required=True,
    #     default=f"{pathlib.Path(__file__).parent / 'db'/ 'who_v2_catalog.csv'}"
    # )
    # parser_sub_search.add_argument(
    #     '--catalog_config',
    #     '-cfg',
    #     # required=True,
    #     help = "json file indicating the relevant column settings for interpretation of the catalog file.",
    #     default= f"{pathlib.Path(__file__).parent / 'configs'/ 'db_config.json'}"
    # )
    # parser_sub_search.add_argument(
    #     '--query',
    #     '-q',
    #     required=True,
    #     nargs='+',
    #     help="The term and column to search. Example rifampicin drug - this will search for rifampicin in the drug column"
    # )
    # parser_sub_search.set_defaults(func = search_catalog)
    parser_sub_predict.set_defaults(func=run_predict)
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
