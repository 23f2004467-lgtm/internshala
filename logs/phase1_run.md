Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
=== Routing eval ===
Loading weights:   0%|          | 0/199 [00:00<?, ?it/s]Loading weights: 100%|██████████| 199/199 [00:00<00:00, 5102.56it/s]
  threshold    TP    FP    FN    precision    recall     F1
-----------  ----  ----  ----  -----------  --------  -----
       0.4     42    30     0        0.583     1      0.737
       0.45    40    24     2        0.625     0.952  0.755
       0.5     37    13     5        0.74      0.881  0.804
       0.55    24     4    18        0.857     0.571  0.686
       0.6      9     0    33        1         0.214  0.353
       0.62     6     0    36        1         0.143  0.25
       0.65     3     0    39        1         0.071  0.133
       0.7      0     0    42        0         0      0
       0.75     0     0    42        0         0      0
       0.8      0     0    42        0         0      0
       0.85     0     0    42        0         0      0

Best F1 at threshold = 0.5 (F1 = 0.804)
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.

=== Demo: routing for example post ===
Post: OpenAI just released a new model that might replace junior developers.

Loading weights:   0%|          | 0/199 [00:00<?, ?it/s]Loading weights: 100%|██████████| 199/199 [00:00<00:00, 5510.33it/s]
Tech Maximalist (score=0.655) — matched facet: Artificial intelligence and machine learning will solve major human problems and replace inefficient labor.
Doomer / Skeptic (score=0.602) — matched facet: AI development is reckless, displaces workers, and harms artists and creators.
Finance Bro (score=0.588) — matched facet: Algorithmic and quantitative trading strategies, alpha generation, and market microstructure.
