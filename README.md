# mutAMR

## Motivation

**Why oh why another variant detection tool? I hear you ask.** There are many high quality tools for reporting of variants from microbial paired-end sequencing, including but not limited to [snippy](https://github.com/tseemann/snippy) and [gatk](https://gatk.broadinstitute.org/hc/en-us). If you require SNP calling for phylogentics or core genome analysis I recommend that you use these tools. 

However, there are cases where a simple vcf is all that is required, in particular for use in identification of acquired AMR mechanims. In addition, many tools which identify SNPs or deletions for AMR are part of large scale tools which, whilst are high quality and extremely useful, they can be complex to install, due to dependencies and run.

`mutAMR` was written to address a very simple need - generation of a single file as output that can be used for identification of variant for AMR. It is designed to be a very simple tool - that simply and specifically generates a vcf file from paired-end illumina reads. It is a stripped down tool - using [bwa-mem](https://github.com/lh3/bwa), [freebayes](https://github.com/freebayes/freebayes), [delly](https://github.com/dellytools/delly) and [samtools](http://www.htslib.org/) and is inspired by [snippy](https://github.com/tseemann/snippy).

Further functions may be introduced overtime (for example variant calling amplicon based sequencing or for specific genes) if others do not write a more useful tool!!


## What `mutAMR` is NOT?

`mutAMR` is **NOT** a

* Pipeline to provide hands off interpretations for AMR. If you require a tool like that - please use `tbtAMR`, `mykrobe` or `TB-Profiler`
* Tool designed for generation of alignments suitable for phylogenetic or core-genome analysis. If you require a tool like this - please use [`snippy`](https://github.com/tseemann/snippy) 

## Assumptions

When designing `mutAMR` I have made some assumptions about the setup, inputs and user requirements.

1. Paired-end fastq files
    
    a. It is assumed that these reads are generated from the species from which you supply a reference genome.

    b. That the reads are of sufficient quality for generation of alignments

2. The user does not want to retain any intermediary files, such as `.bam` (you can retain these files if you like - see below for how to use).

3. If running from the commandline `mutAMR` is being run on a per-sample basis. If you want to run it on more than one sample:

    a. Use a workflow language such as `nextflow` or `snakemake` - recommended.

    b. Use `parallel` (see below for suggested format).

    c. Use a for-loop to iterate over your collection.

3. `delly` is installed properly and you want to detect large deletions in your sequences. If not - only small deletions will be detected by freebayes - which is capable of accurately recovering deletions up to ~50-75 bp.

4. `snpEff` is installed properly with available configs. If not - no annotation will occur, you will need to annotate your `vcf` separately.

## Dependencies

`mutAMR` is a python package that runs

* `bwa-mem` to align reads to reference genome
* `freebayes` to identify variants. Note variants will be identified down to the minimum fraction designated by the user (default 0.1), see Running mutAMR.
* If installed, `delly` will be used to identify large deletions. If not installed - then small deletions will be reported as detected by `freebayes`. A combined vcf file will be generated, combining the variants detected by `freebayes` and `delly`.
* Annotation will be undertaken using `snpEff`, to allow for simple integration with the WHO _M. tuberculosis_ catalogue V2.


## Validation

`mutAMR` has been validated for detection of SNPS in _M. tuberculosis_ for the purposes of AMR mechanism detection. The default settings for `mutAMR` 

* Default min depth for base calling in `mutAMR` is 20 reads. This is higher than what is more commonly used (10 reads). This is because when calling lower frequency mutations (<90% allele frequency), using 10 reads resulted in more false positive variant detection. Which can potentially lead to false calling of resistance.

* Min allele frequency is set to 0.1 in order to capture low frequency mutations. Allele frequencies lower than 0.1 also resulted in false postive SNP. 

Validation results are published TBC.

## Installation

### Conda - recommended

It is highly recommended to install `mutAMR` using `conda` in order to prevent dependency clashes and other issues that may arise - especially if using a share computing resource.

`mutAMR` can be installed as a conda package with all dependencies.

```
conda create -n mutamr mutamr
```

Or you can download the `environment.yml` file from the root of this repository and 

```
conda env create -f environment.yml
```

### Manual installation

At a minimum you need to make sure that the required dependencies have been installed. The versions specified below have all been confirmed to work together and not cause any installation issues or unexpected behaviour. If you decide to use other versions - please be aware that behaviour may not be as described. For example `samtools` version 1.21 can cause issues, whilst version 1.20 does not.

#### Required

* python ==3.10
* samtools ==1.20 
* bcftools ==1.20
* freebayes ==1.3.8
* bwa mem ==0.7.18

#### Optional
* delly ==1.2.8
* snpEff ==5.2

## Using `mutAMR`

`mutAMR` can be used from the commandline - or as an importable package to run as part of another python package.

### Import

Below is an example of using `mutAMR` as part of an another python script or tool

**Required arguments**

* `read1`
* `read2`

**Optional**

* `reference` (if you are using `mutAMR` for _M. tuberculosis_ you can simple set `mtb=True` no need to use this argument)
    * in fasta format
* `annotation` this is the species for `snpEff`  (if you are using `mutAMR` for _M. tuberculosis_ you can simple set `mtb=True` no need to use this argument)
* `threads`
    * default = 8
* `ram`
    * default = 8
* `keep` - boolean argument - if you would like to keep all intermediary file (inlcuding bam) set to True
    * default = False
* `mtb` - boolean argument - if set to True reference and annotation species will be automatically set
    * default = False
* `mindepth` - the minimum depth required for base calling. The default is higher than standard (10) to improve the performance of base calling at low `minfrac`
    * default = 20
* `minfrac` - the lowest allele frequency to call a SNP.
    * defaul = 0.1
* `force` - if the output folder already exists - `mutAMR` will stop to prevent accidental overwriting of data. If you would like to override existing `mutAMR` outputs set `force=True`
    * default = False
* `tmp` - the tmp directory for `samtools` - use of this can improve performance
    * default = `/tmp/username`


**Example for running _M. tuberculosis_**

```
from mutamr import Fastq2vcf

read1 = "/path/read1.fastq.gz"
read1 = "/path/read2.fastq.gz"
seq_id= "sample_name"
mtb = True
keep = True

V = Fastq2vcf.Fastq2Vcf(
                read1 = read1,
                read2= read2,
                seq_id= seq_id,
                keep = keep,
                mtb = mtb
                )
vcf = V.run()
```

This will generate a vcf file at `sample_name/sample_name.annot.vcf.gz`, the variable `vcf` is a string and contains the path to the vcf file for input into other tools or functions.

### CLI

`mutAMR` can also be run from the commandline

**Example for running _M. tuberculosis_**
```
mutamr wgs -1 /path/read1.fastq.gz -2 /path/read2.fastq.gz -s sample_name --mtb --keep
```
This will generate the same files as above, keeping all intermediary files.

#### parallel

As stated above ideally if you would like to run `mutAMR` on a batch of sequences you can use a workflow language or `parallel`. An example of `parallel` is below.

```
parallel --colsep '\t' -j 8 mutamr wgs -1 {2} -2 {3} -s {1} --mtb :::: reads.txt
```

where `reads.txt` is a tab-delimited file containing 3 columns

1. Sequence ID
2. Path to R1
3. Path to R2
