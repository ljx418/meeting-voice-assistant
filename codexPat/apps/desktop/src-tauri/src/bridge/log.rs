use std::collections::VecDeque;

const EVENT_LOG_CAPACITY: usize = 50;

#[derive(Clone)]
pub struct RingBuffer<T> {
    items: VecDeque<T>,
    capacity: usize,
}

impl<T: Clone> RingBuffer<T> {
    pub fn new(capacity: usize) -> Self {
        Self {
            items: VecDeque::with_capacity(capacity),
            capacity,
        }
    }

    pub fn push(&mut self, item: T) {
        if self.items.len() >= self.capacity {
            self.items.pop_front();
        }
        self.items.push_back(item);
    }

    pub fn latest_first(&self) -> Vec<T> {
        self.items.iter().rev().cloned().collect()
    }

    pub fn last(&self) -> Option<T> {
        self.items.back().cloned()
    }
}

impl<T: Clone> Default for RingBuffer<T> {
    fn default() -> Self {
        Self::new(EVENT_LOG_CAPACITY)
    }
}
