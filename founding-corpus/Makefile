PY:=python

all: download normalize dedup shard train-tokenizer report

permissive:
	$(MAKE) download ALLOW_NC=false
	$(MAKE) normalize
	$(MAKE) dedup
	$(MAKE) shard
	$(MAKE) train-tokenizer
	$(MAKE) report

download:
	$(PY) scripts/load_founders_online.py --years configs/years.yml --out data_raw/founders_online --allow-nc $${ALLOW_NC:-true}
	$(PY) scripts/load_tcp.py --corpus evans --years configs/years.yml --out data_raw/evans_tcp
	$(PY) scripts/load_tcp.py --corpus ecco --years configs/years.yml --out data_raw/ecco_tcp
	$(PY) scripts/load_tcp_public.py --years configs/years.yml --out data_raw/tcp_public
	$(PY) scripts/load_historical_legal.py --start-year 1777 --end-year 1797 --out data_raw/historical_legal
	$(PY) scripts/load_american_stories.py --years configs/years.yml --out data_raw/american_stories
	$(PY) scripts/load_old_bailey.py --years configs/years.yml --out data_raw/old_bailey --allow-nc $${ALLOW_NC:-true}
	$(PY) scripts/load_gutenberg_texts.py --ids configs/gutenberg_ids.txt --out data_raw/gutenberg
	$(PY) scripts/load_blbooks.py --out data_raw --year-min 1730 --year-max 1779

normalize:
	$(PY) scripts/normalize.py --in-dir data_raw --out data_clean

dedup:
	$(PY) scripts/dedup.py --in data_clean --out data_dedup --prefer permissive-first

shard:
	$(PY) scripts/shard.py --in data_dedup/corpus_all.jsonl --out data_dedup/shards --target-mb 75

train-tokenizer:
	$(PY) scripts/train_tokenizer.py --shards data_dedup/shards --out reports/tokenizer --vocab-size 30000 --cased

report:
	$(PY) scripts/report.py --clean data_clean --dedup data_dedup --tok reports/tokenizer
