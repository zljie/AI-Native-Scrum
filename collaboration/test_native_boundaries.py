"""Synthetic event negatives only; these tests cannot establish live host proof."""
import unittest
from codex_adapter import NativeProof
from agent_collaboration import Fault


class NativeBoundaryTests(unittest.TestCase):
    def event(self, tool, child='child', parent='parent'):
        return {'type': 'collabAgentToolCall', 'id': tool + '-' + child + '-fixture',
                'status': 'completed', 'senderThreadId': parent,
                'receiverThreadIds': [child], 'tool': tool,
                'agentsStates': {child: {'status': 'completed'}}}

    def test_foreign_parent_cannot_supply_spawn_or_completion(self):
        for tool in ('spawn_agent', 'wait'):
            proof = NativeProof('parent')
            proof.observe(self.event('spawn_agent', parent='foreign' if tool == 'spawn_agent' else 'parent'))
            proof.observe(self.event('wait', parent='foreign' if tool == 'wait' else 'parent'))
            with self.assertRaisesRegex(Fault, 'NATIVE_CHILD_NOT_VERIFIED'):
                proof.evidence()

    def test_wait_before_spawn_cannot_be_replayed_as_completion(self):
        proof = NativeProof('parent')
        proof.observe(self.event('wait'))
        proof.observe(self.event('spawn_agent'))
        with self.assertRaisesRegex(Fault, 'NATIVE_CHILD_NOT_VERIFIED'):
            proof.evidence()
        proof.observe({**self.event('wait'), 'id': 'fresh-wait-fixture'})
        self.assertEqual(proof.evidence(), 'child')

    def test_unfinished_second_child_invalidates_single_child_scope(self):
        proof = NativeProof('parent')
        proof.observe(self.event('spawn_agent'))
        proof.observe(self.event('wait'))
        proof.observe(self.event('spawn_agent', child='second'))
        with self.assertRaisesRegex(Fault, 'NATIVE_CHILD_SCOPE_MISMATCH'):
            proof.evidence()

    def test_exact_duplicate_notifications_do_not_create_extra_child(self):
        proof = NativeProof('parent')
        for tool in ('spawn_agent', 'spawn_agent', 'wait', 'wait'):
            proof.observe(self.event(tool))
        self.assertEqual(proof.evidence(), 'child')
        self.assertEqual(len(proof.spawned), 1)
        self.assertEqual(len(proof.waited), 1)

    def test_replayed_early_wait_cannot_supply_late_completion(self):
        proof = NativeProof('parent')
        early = self.event('wait')
        proof.observe(early)
        proof.observe(self.event('spawn_agent'))
        proof.observe(early)
        with self.assertRaisesRegex(Fault, 'NATIVE_CHILD_NOT_VERIFIED'):
            proof.evidence()

    def test_changed_identity_cannot_reuse_terminal_event_id(self):
        proof = NativeProof('parent')
        event = self.event('spawn_agent')
        proof.observe(event)
        with self.assertRaisesRegex(Fault, 'NATIVE_EVENT_ID_CONFLICT'):
            proof.observe({**self.event('spawn_agent', child='other'), 'id': event['id']})

    def test_missing_terminal_event_id_cannot_produce_proof(self):
        for bad_id in (None, '', [], {}):
            proof = NativeProof('parent')
            with self.assertRaisesRegex(Fault, 'NATIVE_EVENT_ID_MISSING'):
                proof.observe({**self.event('spawn_agent'), 'id': bad_id})
