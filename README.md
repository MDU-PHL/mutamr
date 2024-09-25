# mutAMR

## Motivation

Why another variant detection tool? There are many high quality tools for reporting of variants from microbial paired-end sequencing, including but not limited to [snippy](https://github.com/tseemann/snippy) and [gatk](https://gatk.broadinstitute.org/hc/en-us). If you require SNP calling for phylogentics or core genome analysis I recommend that you use these tools. 

However, there are cases where a simple vcf is all that is required, in particular for use in identification of acquired AMR mechanims. In addition, many tools which identify SNPs or deletions for AMR are part of large scale tools which, whilst are high quality and extremely useful, they can be complex to install, due to dependencies,and and run.

`mutAMR` was written to address a very simple need - generation of a single file as output that can be used for identification of variant for AMR. It is designed to be a very simple tool - that simply and specifically generates a vcf file from paired-end illumina reads. It is a stripped down tool - using [bwa-mem](https://github.com/lh3/bwa), [freebayes](https://github.com/freebayes/freebayes), [delly](https://github.com/dellytools/delly) and [samtools](http://www.htslib.org/) and is inspired by [snippy](https://github.com/tseemann/snippy).

Further functions may be introduced overtime (for example variant calling amplicon based sequencing or for specific genes) if others do not write a more useful tool!!

## Assumptions

When designing `mutAMR` I have made some assumptions about the setup, inputs and user requirements.

1. Paired-end fastq files
    
    a. It is assumed that these reads are generated from the species from which you supply a reference genome.

    b. That the reads are of sufficient quality for generation of alignments

2. The user does not want to retain any intermediary files, such as `.bam`. If you do wish to retain these files use `--keep`.

3. `mutAMR` is being run on a per-sample basis. If you want to run it on more than one sample:

    a. Use a workflow language such as `nextflow` or `snakemake` - recommended.

    b. Use `parallel` (see wiki for suggested format).

    c. Use a for-loop to iterate over your collection.

3. `delly` is installed properly and you want to detect large deletions in your sequences. If not - only small deletions will be detected by freebayes - which is capable of accurately recovering deletions up to ~50-75 bp.

4. `snpEff` is installed properly with available configs. If not - no annotation will occur, you will need to annotate your `vcf` separately.
