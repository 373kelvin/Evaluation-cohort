// Rust scoring engine.
// Reads ONE Transaction JSON from stdin, writes ONE Score JSON to stdout.
// Pure, deterministic scoring — no I/O inside score(), so it is trivially testable.

use serde::{Deserialize, Serialize};
use std::io::Read;

// We only deserialize the fields the score depends on. serde ignores any
// extra fields (id, currency, status) the service may include — keeps this minimal.
#[derive(Deserialize)]
struct Transaction {
    amount: f64,
    hour: u8,
    country: String,
}

#[derive(Serialize)]
struct Score {
    score: i32,
    reasons: Vec<String>,
}

// Countries we consider low-risk. Anything else adds risk.
const ALLOWLIST: [&str; 3] = ["IN", "US", "GB"];

fn score(txn: &Transaction) -> Score {
    let mut score = 0;
    let mut reasons: Vec<String> = Vec::new();

    if txn.amount > 10000.0 {
        score += 40;
        reasons.push("large amount".to_string());
    }
    if txn.hour <= 4 {
        score += 20;
        reasons.push("unusual hour".to_string());
    }
    if !ALLOWLIST.contains(&txn.country.as_str()) {
        score += 30;
        reasons.push("high-risk country".to_string());
    }

    // Spec: clamp to a max of 100. (With the current rules the max is 90,
    // so this is a safety net if rules are ever added.)
    if score > 100 {
        score = 100;
    }

    Score { score, reasons }
}

fn main() {
    // Read all of stdin.
    let mut input = String::new();
    if let Err(e) = std::io::stdin().read_to_string(&mut input) {
        eprintln!("error: failed to read stdin: {}", e);
        std::process::exit(1);
    }

    // Parse the Transaction. Malformed/empty input -> non-zero exit + stderr.
    let txn: Transaction = match serde_json::from_str(&input) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("error: invalid transaction JSON: {}", e);
            std::process::exit(1);
        }
    };

    let result = score(&txn);

    // Serialize the Score to stdout.
    match serde_json::to_string(&result) {
        Ok(json) => println!("{}", json),
        Err(e) => {
            eprintln!("error: failed to serialize score: {}", e);
            std::process::exit(1);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn txn(amount: f64, hour: u8, country: &str) -> Transaction {
        Transaction { amount, hour, country: country.to_string() }
    }

    #[test]
    fn safe_transaction_scores_zero() {
        // Small daytime domestic txn — no rule fires.
        let s = score(&txn(500.0, 14, "IN"));
        assert_eq!(s.score, 0);
        assert!(s.reasons.is_empty());
    }

    #[test]
    fn large_foreign_night_transaction_scores_high() {
        // The brief's example: amount 12000, hour 3, country RU -> 40+20+30 = 90.
        let s = score(&txn(12000.0, 3, "RU"));
        assert_eq!(s.score, 90);
        assert_eq!(
            s.reasons,
            vec!["large amount", "unusual hour", "high-risk country"]
        );
    }

    #[test]
    fn each_rule_fires_individually() {
        // Only large amount (daytime, domestic).
        assert_eq!(score(&txn(20000.0, 12, "IN")).score, 40);
        // Only unusual hour (small amount, domestic).
        assert_eq!(score(&txn(100.0, 2, "US")).score, 20);
        // Only high-risk country (small amount, daytime).
        assert_eq!(score(&txn(100.0, 12, "FR")).score, 30);
    }

    #[test]
    fn boundaries_are_handled() {
        // amount exactly 10000 is NOT > 10000 -> no large-amount risk.
        assert_eq!(score(&txn(10000.0, 12, "IN")).score, 0);
        // hour exactly 4 is unusual; hour 5 is not.
        assert_eq!(score(&txn(100.0, 4, "IN")).score, 20);
        assert_eq!(score(&txn(100.0, 5, "IN")).score, 0);
    }
}
