"""Public candidate contracts. Validation is stdlib-backed in agent_collaboration."""
from copy import deepcopy
S = {'type': 'string', 'minLength': 1}
REFS = {'type': 'array', 'items': S, 'minItems': 1, 'uniqueItems': True}
ID = {'type': 'string', 'pattern': '^[A-Za-z][A-Za-z0-9_.:-]{0,95}$'}
HASHES = {'type':'object', 'additionalProperties':{'type':'string','pattern':'^[0-9a-f]{64}$'}}

def obj(properties, optional=()):
    return {'type':'object','additionalProperties':False,'properties':deepcopy(properties),
            'required':[k for k in properties if k not in optional]}

def contracts():
    verification = obj({'tests':REFS,'inputs':REFS,'covers':REFS,'command':{'type':'array','items':S,'minItems':1}})
    context = obj({'schema':{'const':'task-context/v1'},'run_id':ID,'goal_ref':S,'story_ref':S,'task_ref':S,
                   'signals':REFS,'signal_evidence':{'type':'object','additionalProperties':REFS},'inputs':REFS,
                   'scopes':{'type':'object','additionalProperties':{'type':'array','items':S}},'authorization_ref':S,
                   'sample_kind':{'enum':['real','fixture']},'verification':verification}, optional=('verification',))
    role = obj({'capabilities':REFS,'contract_ref':S,'profile_ref':S,'enabled':{'type':'boolean'},'priority':{'type':'integer'},'skill_refs':{'type':'array','items':S}}, optional=('skill_refs',))
    registry = obj({'schema':{'const':'agent-capabilities/v1'},'roles':{'type':'object','minProperties':1,'additionalProperties':role}})
    authorization = obj({'schema':{'const':'collaboration-authorization/v1'},'actor':ID,'at':{'type':'string','format':'date-time'},
                         'confirmation_ref':S,'task_refs':REFS,'allow_delegation':{'const':True},'write_paths':REFS,
                         'validation_commands':{'type':'array','items':{'type':'array','items':S,'minItems':1}},
                         'max_attempts':{'type':'integer','minimum':1,'maximum':20},'max_parallel':{'type':'integer','minimum':1,'maximum':8},
                         'sample_kind':{'enum':['real','fixture']}})
    # Handoff payload references existing task truth; no parallel Goal/Story database.
    handoff=obj({'schema':{'const':'collaboration-handoff/v1'},'handoff_id':ID,'revision':{'type':'integer','minimum':1},
                 'supersedes':{'type':['string','null']},'run_id':ID,'work_item_ref':S,'from_delegation':ID,'to_delegation':ID,
                 'from_actor':ID,'to_actor':ID,'base_ref':S,'from_attempt':{'type':'integer','minimum':1},'context_hash':S,
                 'artifacts':HASHES,'objective_ref':S,'acceptance_criteria_refs':REFS,'constraints_ref':S,
                 'decisions':{'type':'array'},'open_issues':{'type':'array'},'risks':{'type':'array'},'checks':{'type':'array'},
                 'evidence_refs':REFS,'required_reviewers':REFS,'next_actions':REFS,
                 'status':{'enum':['submitted','accepted','changes_requested','rejected','superseded']},
                 'created_at':{'type':'string','format':'date-time'},'review':{'type':['object','null']}})
    event=obj({'schema_version':{'const':'1.0'},'event_id':ID,'sequence':{'type':'integer','minimum':1},'event_type':ID,
               'occurred_at':{'type':'string','format':'date-time'},'run_id':ID,'work_item_ref':S,'trace_id':ID,
               'delegation_id':{'type':['string','null']},'agent_instance_ref':{'type':['string','null']},'handoff_id':{'type':['string','null']},
               'actor_type':S,'source_kind':S,'causation_id':{'type':['string','null']},'correlation_id':ID,
               'state_before':{'type':['string','null']},'state_after':{'type':['string','null']},
               'verification_status':{'enum':['verified','reported','unverified','not_applicable']},
               'evidence_refs':{'type':'array','items':S},'artifact_refs':{'type':'array','items':S},
               'payload':obj({'reason':{'type':['string','null']}}),'sample_kind':{'enum':['real','fixture']}})
    return {name:{'$schema':'https://json-schema.org/draft/2020-12/schema', 'title':name,**value}
            for name,value in [('task-context',context),('registry',registry),('authorization',authorization),('handoff',handoff),('event',event)]}
