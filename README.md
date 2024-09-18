# mutAMR

## Motivation

Why another variant detection tool? There are many high quality tools for reporting of variants from microbial paired-end sequencing, including but not limited to [snippy](https://github.com/tseemann/snippy) and [gatk](https://gatk.broadinstitute.org/hc/en-us). If you require SNP calling for phylogentics or core genome analysis I recommend that you use these tools. 

However, there are cases where a simple vcf is all that is required, in particular for use in identification of acquired AMR mechanims. In addition, many tools which identify SNPs or deletions for AMR are part of large scale tools which, whilst these are also high quality, they can be complex to install, due to dependencies,and and run.

`mutAMR` is designed to be a very simple tool - that simply and specifically generates a vcf file from paired-end illumina reads. It is a stripped down tool - using bwa-mem, freebayes, delly and samtools and is inspired by snippy.

Further functions may be introduced overtime (for example variant calling amplicon based sequencing or for specific genes) if others do not write a more useful tool!!