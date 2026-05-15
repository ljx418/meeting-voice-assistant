use std::{
    collections::{HashMap, VecDeque},
    time::{Duration, Instant},
};

const WINDOW: Duration = Duration::from_secs(10);
const GLOBAL_LIMIT: usize = 30;
const SOURCE_LIMIT: usize = 10;

#[derive(Default)]
pub struct RateLimiter {
    global: VecDeque<Instant>,
    by_source: HashMap<String, VecDeque<Instant>>,
}

impl RateLimiter {
    pub fn check(&mut self, source_id: &str) -> Result<(), String> {
        let now = Instant::now();
        prune(&mut self.global, now);
        if self.global.len() >= GLOBAL_LIMIT {
            return Err("global rate limit exceeded".to_string());
        }

        let source_events = self.by_source.entry(source_id.to_string()).or_default();
        prune(source_events, now);
        if source_events.len() >= SOURCE_LIMIT {
            return Err("source rate limit exceeded".to_string());
        }

        self.global.push_back(now);
        source_events.push_back(now);
        Ok(())
    }
}

fn prune(events: &mut VecDeque<Instant>, now: Instant) {
    while events
        .front()
        .map(|created_at| now.duration_since(*created_at) > WINDOW)
        .unwrap_or(false)
    {
        events.pop_front();
    }
}
