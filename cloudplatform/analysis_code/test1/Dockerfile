FROM simonalpha/ncbi-blast-docker

ADD query.fasta /blast/

CMD blastp -db /db/ncbi_nr/nr -query query.fasta -out /results/results.out