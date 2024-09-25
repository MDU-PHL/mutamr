import subprocess,pathlib,os, sys,logging
from .CustomLog import logger



class Fastq2Vcf(object):

    def __init__(self,
                 read1,
                 read2,
                 threads=8,
                 ram= 8,
                 seq_id = "mutamr",
                 reference = "",
                 annotation = "",
                 keep = True,
                 mtb = False,
                 mindepth = 20,
                 minfrac = 0.1,
                 force = False,
                 tmp = f"{pathlib.Path(tempfile.gettempdir())}"
                 ):
        
        self.read1 = read1
        self.read2 = read2
        self.mtb = mtb
        self.threads = int(threads)
        self.ram = int(ram)
        self.seq_id = seq_id if seq_id != "" else 'mutamr'
        self.reference = f"{pathlib.Path(__file__).parent / 'references'/ 'Mtb_NC000962.3.fa'}" if mtb else reference
        self.species = "Mycobacterium_tuberculosis_h37rv" if mtb else annotation
        self.keep = keep
        self.mindepth= mindepth
        self.minfrac = minfrac
        self.force = force
        self.tmp = tmp
        self.essential_tools = ['bwa', 'freebayes-parallel', 'samtools', 'bcftools', 'samclip']
        self.optional_tools = ['delly', 'snpEff']
        self.to_remove = [
            "ref.txt",
            f"{self.seq_id}.bam",
            f"{self.seq_id}.raw.snps.vcf",
            f"{self.seq_id}.delly.vcf",
            f"{self.seq_id}.delly.bcf",
            f"{self.seq_id}.concat.vcf",
            f"{self.seq_id}.snps.vcf"
        ]
        self.create_output_dir(seq_id=self.seq_id, force= self.force)
        fh = logging.FileHandler(f'{seq_id}/mutamr.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s:%(asctime)s] %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p') 
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    def check_file(self,pth):

        logger.info(f"Checking {pth} exists")
        if pathlib.Path(pth).exists():

            return True
        else:

            logger.critical(f"{pth} does not exist. Please try again.")
        raise SystemExit

    def run_cmd(self, cmd) -> bool:

        logger.info(f"Now running {cmd}")

        proc = subprocess.run(cmd, shell = True, capture_output=True, encoding='utf-8')

        if proc.returncode == 0:
            logger.info(f"{proc.stdout}")
            return True
        else:
            logger.warning(f"{cmd} failed. The following error was encountered : {proc.stderr} | {proc.stdout}")
            return False


    def check_tool(self, tool, essential = True) -> bool:

        paths = os.getenv('PATH').split(':')
        for pth in paths:
            d = pathlib.Path(pth)
            tl = d /f"{tool}"
            if tl.exists():
                logger.info(f"{tool} installed.")
                return True
        
        
        if essential:
            logger.critical(f"{tool} could not be found - please check your installation and try again. mutAMR cannot be run - Exiting...")
            sys.exit(0)
        logger.warning(f"{tool} could not be found - please check your installation. {tool} will not be run")
        return False

    def check_installation(self) -> bool:

        for tool in self.essential_tools:
            self.check_tool(tool = tool)
                
        for tool in self.optional_tools:
            self.check_tool(tool = tool, essential = False)

        return True



    def get_stats(self, bam) -> bool:
        
        
        cmd = f"samtools coverage {bam} > {self.seq_id}/{self.seq_id}_stats.txt"

        self.run_cmd(cmd = cmd)

        return True

    def align(self,r1,r2,seq_id,ref,threads,rams, tmp,keep = False) -> bool:

        logger.info("Generating alignment using bwa mem.")
        cpu = max(1, int(threads))
        ram = int(1000*rams/cpu)
        tmp_dir = f'-T {tmp}' if tmp != '' else ''
        bwa = f"bwa mem -T 50 -Y -M -R '@RG\\tID:{seq_id}\\tSM:{seq_id}' -t {cpu} {ref} {r1} {r2} | \
samclip --max 10 --ref {ref}.fai | samtools sort -n -l 0 -@ {cpu} -m {ram}M {tmp_dir} | \
samtools fixmate -m - - | samtools sort -l 0 -@ {cpu} -m {ram}M {tmp_dir} | \
samtools markdup {tmp_dir} -r -s - - > {seq_id}/{seq_id}.bam"
        
        bproc = self.run_cmd(cmd = bwa)
        if bproc:
            logger.info(f"Indexing bam")
            idx = self.run_cmd(cmd = f"samtools index {seq_id}/{seq_id}.bam")
            if idx:
                self.get_stats(bam = f"{seq_id}/{seq_id}.bam")
                return True
        return False

    def freebayes(self,seq_id,ref, threads, mindepth = 20, minfrac= 0.1 ) -> str:
        logger.info(f"Calculating sizes for freebayes-parallel")
        # Thanks to Torsten Seemann snippy code!!
        with open(ref, 'r') as r:
            l = r.read()
        ref_len = len(l)
        logger.info(f'Reference is {ref_len} in length')
        chunks = 1 + 2*(threads-1)
        chunk_size = max(1000, int(ref_len/chunks))
        logger.info(f"Reference will be broken into {chunks} chunks approx {chunk_size} in size")
        fgr = f"fasta_generate_regions.py {ref} {chunk_size} > {seq_id}/ref.txt"
        self.run_cmd(fgr)
        logger.info("Running freebayes for SNP detection.")
        fb = f"freebayes-parallel {seq_id}/ref.txt {threads} -q 13 -m 60 -f {ref} -F {minfrac} --haplotype-length -1 {seq_id}/{seq_id}.bam > {seq_id}/{seq_id}.raw.snps.vcf"
        # fb = f"freebayes "
        fltr = f"bcftools view -c 1 {seq_id}/{seq_id}.raw.snps.vcf | bcftools norm -f {ref} | bcftools filter -e 'FMT/DP<{mindepth}'  -Oz -o {seq_id}/{seq_id}.snps.vcf.gz"
        idx = f"bcftools index {seq_id}/{seq_id}.snps.vcf.gz"
        # logger.info(f"Running freebayes")
        if self.run_cmd(cmd = fb):
            logger.info(f"Filtering vcf")
            if self.run_cmd(cmd = fltr):
                logger.info(f"Indexing vcf")
                if self.run_cmd(cmd = idx):
                    return f"{seq_id}/{seq_id}.snps.vcf.gz"
        
        logger.critical(f"Freebayes did not complete successfully! Please check log file and try again.")
        raise SystemExit
    
    def delly(self,ref, seq_id, threads) -> bool:

        logger.info(f"Running delly")
        delly = f"OMP_NUM_THREADS={threads} delly call -t DEL -g {ref} {seq_id}/{seq_id}.bam -o {seq_id}/{seq_id}.delly.bcf"
        gz = f"bcftools view -c 2 {seq_id}/{seq_id}.delly.bcf | bcftools view -e '(INFO/END-POS)>=100000' -Oz -o {seq_id}/{seq_id}.delly.vcf.gz"
        idx = f"bcftools index {seq_id}/{seq_id}.delly.vcf.gz"
        
        logger.info(f"Running delly")
        if self.run_cmd(cmd = delly):
            logger.info(f"Filtering vcf")
            if self.run_cmd(cmd = gz):
                logger.info(f"Indexing vcf")
                if self.run_cmd(cmd = idx):
                    return True
        return False

    def combine_vcf(self,seq_id) -> str:
        logger.info(f"Combining vcf files")
        concat = f"bcftools concat -aD {seq_id}/{seq_id}.delly.vcf.gz {seq_id}/{seq_id}.snps.vcf.gz | bcftools norm -m -both | bcftools view -W -Oz -o {seq_id}/{seq_id}.concat.vcf.gz"
        self.run_cmd(cmd = concat)
        return  f"{seq_id}/{seq_id}.concat.vcf.gz"
    
    def annotate(self, vcf) -> str:
        logger.info(f"Wrangling snpEff DB")
        p = os.environ.get('CONDA_PREFIX').strip('bin')
        cfg = sorted(pathlib.Path(p,'share').glob('snpeff*/snpEff.config'))
        if cfg != []:
            cfg_path = cfg[0]
            snpeff =f"snpEff ann -dataDir . -c {cfg_path} -noLog -noStats {self.species} {vcf} > {self.seq_id}/{self.seq_id}.annot.vcf"
            logger.info(f"Annotating vcf file")
            self.run_cmd(cmd=snpeff)
            self.run_cmd(cmd = f"bgzip -f {self.seq_id}/{self.seq_id}.annot.vcf")
            self.run_cmd(cmd = f"bcftools index {self.seq_id}/{self.seq_id}.annot.vcf.gz")
            return f"{self.seq_id}/{self.seq_id}.annot.vcf.gz"
        else:
            logger.info(f"Cannot annotate the file {self.seq_id}.concat.vcf.gz - as it appears that snpEff is not corrctly installed.")
            return vcf      

    
    def clean_up(self, vcf):
        
        target = f"{vcf}"
        logger.info(f"Will now clean up directory, keeping {target}.")
        
        for fl in self.to_remove:
            fls = [f"{f}" for f in sorted(pathlib.Path(f"{self.seq_id}").glob(f"{fl}*"))]
            if f"{fl}" not in f"{target}" and fls != []:
                logger.warning(f"Will now remove {' '.join(fls)}")
                rm = f"rm -f {' '.join(fls)}"
                # logger.warning(f"Running : {rm}")
                self.run_cmd(cmd = rm)

    def create_output_dir(self,seq_id, force = False) -> bool:

        cmd = f"mkdir -p {seq_id}"
        if pathlib.Path(f"{seq_id}").exists() and not force:
            logger.critical(f"{seq_id} already exists. If you would like to over write please re-run with --force.")
            raise SystemExit
        
        logger.info(f"Will now create directory for {seq_id}")
        proc = self.run_cmd(cmd = cmd)
        if proc:
            return True
        
        return False
    
    def run(self):

        self.check_installation()

        if self.check_file(pth=self.reference) and self.check_file(pth = self.read1) and self.check_file(pth=self.read2) and self.seq_id != "":
            
            if self.align(r1 = self.read1, r2= self.read2, seq_id=self.seq_id, ref = self.reference, threads= self.threads, rams = self.ram, tmp=self.tmp):
                logger.info(f"Alignment was successful!")
                vcf = self.freebayes(seq_id=self.seq_id, ref= self.reference, mindepth= self.mindepth, minfrac=self.minfrac, threads = self.threads)
                logger.info(f"Freebayes was successful!!")
                if self.delly(ref = self.reference, seq_id= self.seq_id, threads = self.threads):
                    vcf = self.combine_vcf(seq_id= self.seq_id)
                vcf = self.annotate(vcf = vcf)
                if not self.keep:
                    self.clean_up(vcf = vcf)
                
                return vcf
        else:
            logger.critical(f"Something has gone wrong! Please check your inputs and try again.")
            raise SystemExit