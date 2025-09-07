Questa directory contiene i file PDF da preprocessare con Docling.

I PDF collocati qui verranno automaticamente convertiti in formato Markdown 
e spostati nella directory /documents per il successivo ingesting nel vector store.

Per avviare il preprocessing:
python preprocess.py

Per il pipeline completo (preprocessing + ingesting):
python full_pipeline.py