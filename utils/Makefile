SOURCE_DIR = ../src
TEMP_DIR = temp_work_dir
OUTPUT_DIR = ../MPO
DOC_DIR = ../docs

DOC_BLACKLIST = __init__

.PHONY: all program pydoc

all: program pydoc

program: $(OUTPUT_DIR)/MPO.pyz

pydoc: $(DOC_DIR)/dokumentation/MPO.html

$(OUTPUT_DIR)/MPO.pyz: $(SOURCE_DIR)/__main__.py $(SOURCE_DIR)/MPO/*.py
	mkdir -p $(TEMP_DIR)/MPO;
	cp -r $(SOURCE_DIR)/* $(TEMP_DIR)/MPO/;
	cd $(TEMP_DIR); \
	python3 -m zipapp -c MPO;
	mv $(TEMP_DIR)/$(notdir $@) $@;
	rm -r $(TEMP_DIR);

$(DOC_DIR)/dokumentation/MPO.html: $(SOURCE_DIR)/MPO/*.py
	mkdir -p $(TEMP_DIR)/MPO;
	cp -r $(SOURCE_DIR)/MPO/* $(TEMP_DIR)/MPO/;
	cd $(TEMP_DIR); \
	pydoc -w MPO; \
	sed -i 's:<a href=".".*</a>::' MPO.html; \
	for pyfile in $(basename $(notdir $^)); do \
	   pydoc -w MPO.$$pyfile; \
	   sed -i "s:<font color=\"#ffffff\" face=\"helvetica, arial\"><a href=\".\">index</a>.*.py</a></font>::g;s:<a href=\"file.*</a>::g" MPO.$$pyfile.html; \
	done; \
	for blacklisted in $(DOC_BLACKLIST); do \
	   sed -i "s:<a href=\"MPO.$$blacklisted.html\">$$blacklisted</a><br>:<i>$$blacklisted</i><br>:" MPO.html; \
	   rm MPO.$$blacklisted.html; \
	done;
	mv $(TEMP_DIR)/*.html $(DOC_DIR)/;
	rm -r $(TEMP_DIR);
