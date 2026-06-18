# Engine — Rust scoring CLI

Reads one Transaction JSON from **stdin**, writes one Score JSON to **stdout**.

## Build & test

```bash
cd engine
cargo build --release      # binary -> target/release/engine
cargo test                 # 4 tests
```

## Use

```bash
echo '{"amount":12000,"currency":"INR","hour":3,"country":"RU"}' \
  | ./target/release/engine
# -> {"score":90,"reasons":["large amount","unusual hour","high-risk country"]}
```

## Rules (deterministic, pure)

| Condition | Points | Reason |
|-----------|-------|--------|
| `amount > 10000` | +40 | large amount |
| `hour` 0–4 | +20 | unusual hour |
| `country` not in `[IN, US, GB]` | +30 | high-risk country |

Final score clamped to a max of 100. Malformed/empty stdin → non-zero exit
+ stderr message.
