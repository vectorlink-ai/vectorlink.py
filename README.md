# vectorlink.py

## dedup + embed plan
1. write a deduped hash+string table
2. have these tables:
   1. hash+string
   2. hash+embedding
3. do an anti-join to find everything in 1 that is not in 2
4. batch up and send to openai
5. store results in 2
