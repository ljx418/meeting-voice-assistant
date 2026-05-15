use super::protocol::AcceptedPetEvent;
use std::collections::VecDeque;

pub const INGRESS_QUEUE_CAPACITY: usize = 32;

#[derive(Clone)]
pub struct QueuedEvent {
    pub event_id: String,
    pub event: AcceptedPetEvent,
    pub emitted: bool,
}

#[derive(Default)]
pub struct IngressQueue {
    pending: VecDeque<QueuedEvent>,
    capacity: usize,
}

impl IngressQueue {
    pub fn new(capacity: usize) -> Self {
        Self {
            pending: VecDeque::with_capacity(capacity),
            capacity,
        }
    }

    pub fn capacity(&self) -> usize {
        self.capacity
    }

    pub fn len(&self) -> usize {
        self.pending.iter().filter(|event| !event.emitted).count()
    }

    pub fn admit(&mut self, queued: QueuedEvent) -> Result<QueueAdmission, QueueReject> {
        if should_merge(&queued.event.level) {
            if let Some(existing) = self.pending.iter_mut().find(|event| {
                !event.emitted
                    && event.event.source.id == queued.event.source.id
                    && event.event.level == queued.event.level
            }) {
                *existing = queued;
                return Ok(QueueAdmission::Merged);
            }
        }

        self.prune_emitted();
        if self.pending.len() >= self.capacity {
            return Err(QueueReject::Full);
        }

        self.pending.push_back(queued);
        Ok(QueueAdmission::Queued)
    }

    pub fn mark_emitted(&mut self, event_id: &str) {
        if let Some(event) = self
            .pending
            .iter_mut()
            .find(|event| event.event_id == event_id)
        {
            event.emitted = true;
        }
        self.prune_emitted();
    }

    fn prune_emitted(&mut self) {
        while self
            .pending
            .front()
            .map(|event| event.emitted)
            .unwrap_or(false)
        {
            self.pending.pop_front();
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum QueueAdmission {
    Queued,
    Merged,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum QueueReject {
    Full,
}

fn should_merge(level: &str) -> bool {
    matches!(level, "thinking" | "running")
}
