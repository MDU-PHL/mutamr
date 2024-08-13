import subprocess,pathlib,os
from CustomLog import logger



class Fastq2Vcf(object):

    def __init__(self,
                 read1,
                 read2,
                 threads,
                 ram,
                 seq_id,
                 reference = "",
                 keep = True,
                 mtb = False,
                 mindepth = 20,
                 minfrac = 0.1,
                 force = False,
                 tmp = ""
                 ):
        
        self.read1 = read1
        self.read2 = read2
        self.threads = int(threads)
        self.ram = int(ram)
        self.seq_id = seq_id if seq_id != "" else 'mutamr'
        self.reference = reference = f"{pathlib.Path(__file__).parent / 'references'/ 'Mtb_NC000962.3.fa'}" if mtb else reference
        self.keep = keep
        self.mtb = mtb
        self.mindepth= mindepth
        self.minfrac = minfrac
        self.force = force
        self.tmp = tmp

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
            logger.critical(f"{cmd} failed. The following error was encountered : {proc.stderr}")
            raise SystemExit

    def align(self,r1,r2,seq_id,ref,threads,rams, tmp,keep = False) -> bool:

        logger.info("Generating alignment using bwa mem.")
        cpu = max(1, int(threads))
        ram = int(1000*rams/cpu)
        tmp_dir = f'-T {tmp}' if tmp != '' else ''
        bwa = f"bwa mem -T 50 -Y -M -R '@RG\\tID:{seq_id}\\tSM:{seq_id}' -t {cpu} {ref} {r1} {r2} | \
samclip --max 10 --ref {ref}.fai | samtools sort -n -l 0 --threads {cpu} -m {ram}M {tmp_dir} \
| samtools fixmate -m - - | samtools sort -l 0  --threads {cpu} -m {ram}M {tmp_dir} \
| samtools markdup {tmp_dir} -r -s - - > {seq_id}/{seq_id}.bam"
        
        bproc = self.run_cmd(cmd = bwa)
        logger.info(f"Indexing bam")
        self.run_cmd(cmd = f"samtools index {seq_id}/{seq_id}.bam")


    def freebayes(self,seq_id,ref, threads, mindepth = 20, minfrac= 0.1 ) -> bool:
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
        self.run_cmd(cmd = fb)
        logger.info(f"Filtering vcf")
        self.run_cmd(cmd = fltr)
        logger.info(f"Indexing vcf")
        self.run_cmd(cmd = idx)
        return True
    
    def delly(self,ref, seq_id) -> bool:

        logger.info(f"Running delly")
        delly = f"delly call -t DEL -g {ref} {seq_id}/{seq_id}.bam -o {seq_id}/{seq_id}.delly.bcf"
        gz = f"bcftools view -c 2 {seq_id}/{seq_id}.delly.bcf | bcftools view -e '(INFO/END-POS)>=100000' -Oz -o {seq_id}/{seq_id}.delly.vcf.gz"
        idx = f"bcftools index {seq_id}/{seq_id}.delly.vcf.gz"

        logger.info(f"Running delly")
        self.run_cmd(cmd = delly)
        logger.info(f"Filtering vcf")
        self.run_cmd(cmd = gz)
        logger.info(f"Indexing vcf")
        self.run_cmd(cmd = idx)
        return True 

    def combine_vcf(self,seq_id) -> bool:
        logger.info(f"Combining vcf files")
        concat = f"bcftools concat -aD {seq_id}/{seq_id}.delly.vcf.gz {seq_id}/{seq_id}.snps.vcf.gz | bcftools norm -m -both | bcftools view -W -Oz -o {seq_id}/{seq_id}.concat.vcf.gz"
        self.run_cmd(cmd = concat)
        return True 
    
    def annotate(self, seq_id) -> str:
        logger.info(f"Wrangling snpEff DB")
        p = os.environ.get('CONDA_PREFIX').strip('bin')
        cfg = sorted(pathlib.Path(p,'share').glob('snpeff*/snpEff.config'))
        spc = "Mycobacterium_tuberculosis_h37rv" if self.mtb else ""
        if cfg != []:
            cfg_path = cfg[0]
            snpeff =f"snpEff ann -dataDir . -c {cfg_path} -noLog -noStats {spc} {seq_id}/{seq_id}.concat.vcf.gz > {seq_id}/{seq_id}.annot.vcf"
            logger.info(f"Annotating vcf file")
            self.run_cmd(cmd=snpeff)
            self.run_cmd(cmd = f"bgzip {seq_id}/{seq_id}.annot.vcf")
            self.run_cmd(idx = f"bcftools index {seq_id}/{seq_id}.annot.vcf.gz")
        else:
            logger.info(f"Cannot annotate the file {seq_id}.concat.vcf.gz - as it appears that snpEff is not corrctly installed.")
        
        return f"{seq_id}/{seq_id}.annot.vcf.gz"
    
    def clean_up(self, seq_id):
        
        target = f"{seq_id}/{seq_id}.annot.vcf.gz"

        fls = sorted(pathlib.Path(f"{seq_id}").glob(f"{seq_id}*"))
        for fl in fls:

            if f"{fl}" != f"{target}":
                logger.info(f"Will now remove {fl}")
                # self.run_cmd(cmd = f"rm -f {fl}")

    def create_output_dir(self,seq_id, force = False) -> bool:

        cmd = f"mkdir -p {seq_id}"
        if pathlib.Path(f"{seq_id}/{seq_id}.concat.vcf.gz").exists() and not force:
            logger.critical(f"{seq_id}/{seq_id}.concat.vcf.gz already exists. If you would like to over write please re-run with --force.")
            raise SystemExit
        logger.info(f"Will now create directory for {seq_id}")
        proc = self.run_cmd(cmd = cmd)
        if proc:
            return True
        
        return False
    
    def run(self):

        if self.check_file(pth=self.reference) and self.check_file(pth = self.read1) and self.check_file(pth=self.read2) and self.seq_id != "":
            self.create_output_dir(seq_id=self.seq_id, force= self.force)
            self.align(r1 = self.read1, r2= self.read2, seq_id=self.seq_id, ref = self.reference, threads= self.threads, rams = self.ram, tmp=self.tmp)
            self.freebayes(seq_id=self.seq_id, ref= self.reference, mindepth= self.mindepth, minfrac=self.minfrac, threads = self.threads)
            self.delly(ref = self.reference, seq_id= self.seq_id)
            self.combine_vcf(seq_id= self.seq_id)
            return self.annotate(seq_id=self.seq_id)

        else:
            logger.critical(f"Something has gone wrong! Please check your inputs and try again.")
            raise SystemExit