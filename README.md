# mutAMR

## Motivation

Why another variant detection tool? There are many high quality tools for reporting of variants from microbial paired end sequencing, including but not limited to snippy, gatk. If you require SNP calling for phylogentics or core genome analysis I recommend that you use these tools. 

However, there are cases where a simple vcf is all that is required, in particular for use in identification of acquired AMR mechanims. In addition, many tools whuch identify SNPs or deletions for AMR are part of large scale tools which, whilst are also high quality, may be too large for the simple task of generation of a vcf.

`mutAMR` is designed to be a very simple tool - that simply generates a vcf file from paired-end illumin reads. It is a stripped down tool - using bwa-mem, freebayes, delly and samtools and inspired by snippy.