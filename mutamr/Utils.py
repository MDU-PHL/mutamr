import os,pathlib
from .CustomLog import logger


ESSENTIAL_TOOLS = ['bwa', 'freebayes-parallel', 'samtools', 'bcftools', 'samclip']
OPTIONAL_TOOLS = ['delly', 'snpEff']


def check_tool(tool, essential = True,run = False) -> bool:

        paths = os.getenv('PATH').split(':')
        for pth in paths:
            d = pathlib.Path(pth)
            tl = d /f"{tool}"
            if tl.exists():
                # logger.info(f"{tool} installed.")
                return True
        
        
        
        
        if essential:
            if run:
                logger.critical(f"{tool} could not be found - please check your installation and try again. mutAMR cannot be run - Exiting...")
                sys.exit(0)
        
        logger.warning(f"{tool} could not be found - please check your installation.")
        
        return True

def check_installation(run = False) -> bool:

    
    for tool in ESSENTIAL_TOOLS:
        check_tool(tool = tool, run = run)
            
    for tool in OPTIONAL_TOOLS:
        check_tool(tool = tool, essential = False,run = run)

    
    return True

def check_annotate():

    if check_install(tool = 'snpEff'):
        return True
    else:
        return False



def check_lineage():
    logger.info(f"Will check if lineage can be run.")
    try:
        from pathogenprofiler import barcode, Vcf
        logger.info(f"Lineage calling can be undertaken.")
        return True
    except:
        logger.warning(f"Lineage calling cannot be undertaken - pathogenprofiler needs to be installed.")
        return False
