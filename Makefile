DATA=./data

PY=python3

GEN=$(DATA)/gen
WEBGEN=./web/gen

export NODESPATH=$(DATA)

web: $(WEBGEN)/data.js $(WEBGEN)/data3d.js

$(WEBGEN)/data.js: $(DATA)/nodes.json $(DATA)/times $(DATA)/walk*.txt $(DATA)/rooms*.txt $(DATA)/groups $(DATA)/forks video/gen_choices.py
	@mkdir -p $(@D)
	@$(PY) video/gen_choices.py > $@

$(WEBGEN)/data3d.js: $(DATA)/nodes.json $(GEN)/edge_lengths.pkl $(GEN)/edge_heights.pkl video/gen_3d.py
	@mkdir -p $(@D)
	@$(PY) video/gen_3d.py > $@

$(GEN)/edge_heights.pkl: $(DATA)/nodes.json $(DATA)/times $(DATA)/walk*.txt $(GEN)/edge_lengths.pkl $(DATA)/equal_heights $(DATA)/height_override $(DATA)/rooms*.txt video/elevation.py
	@$(PY) video/elevation.py $@

$(GEN)/edge_lengths.pkl: $(DATA)/nodes.json $(DATA)/times $(DATA)/walk*.txt $(DATA)/equal_nodes $(DATA)/equal_edges video/e2.py
	@mkdir -p $(@D)
	@$(PY) video/e2.py $@
