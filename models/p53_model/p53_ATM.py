# exported from PySB model 'p53_ATM'

from pysb import Model, Monomer, Parameter, Expression, Compartment, Rule, Observable, Initial, MatchOnce, Annotation, ANY, WILD

Model()

Monomer(u'PPM1D', [u'activity'], {u'activity': [u'inactive', u'active']})
Monomer(u'TP53', [u'activity'], {u'activity': [u'inactive', u'active']})
Monomer(u'ATM', [u'activity'], {u'activity': [u'inactive', u'active']})
Monomer(u'HIPK2')
Monomer(u'ARF')
Monomer(u'MDM2', [u'activity'], {u'activity': [u'inactive', u'active']})

Parameter(u'kf_aa_act_1', 5e-06)
Parameter(u'kf_at_act_1', 1e-06)
Parameter(u'kf_tp_act_1', 1e-06)
Parameter(u'kf_tm_act_1', 1e-06)
Parameter(u'kf_pt_act_1', 1e-05)
Parameter(u'kf_pa_act_1', 0.0001)
Parameter(u'kf_mt_act_1', 1e-06)
Parameter(u'kf_hp_act_1', 1e-06)
Parameter(u'kf_am_act_1', 1e-06)
Parameter(u'PPM1D_0', 1000.0)
Parameter(u'TP53_0', 1000.0)
Parameter(u'ATM_0', 1000.0)
Parameter(u'HIPK2_0', 1000.0)
Parameter(u'ARF_0', 1000.0)
Parameter(u'MDM2_0', 1000.0)
Parameter(u'ATMa_0', 1.0)

Observable('p53_active', TP53(activity=u'active'))
Observable('atm_active', ATM(activity=u'active'))

Rule(u'ATM_activates_ATM_activity', ATM(activity=u'active') + ATM(activity=u'inactive') >> ATM(activity=u'active') + ATM(activity=u'active'), kf_aa_act_1)
Rule(u'ATM_activates_TP53_activity', ATM(activity=u'active') + TP53(activity=u'inactive') >> ATM(activity=u'active') + TP53(activity=u'active'), kf_at_act_1)
Rule(u'TP53_activates_PPM1D_activity', TP53(activity=u'active') + PPM1D(activity=u'inactive') >> TP53(activity=u'active') + PPM1D(activity=u'active'), kf_tp_act_1)
Rule(u'TP53_activates_MDM2_activity', TP53(activity=u'active') + MDM2(activity=u'inactive') >> TP53(activity=u'active') + MDM2(activity=u'active'), kf_tm_act_1)
Rule(u'PPM1D_deactivates_TP53_activity', PPM1D(activity=u'active') + TP53(activity=u'active') >> PPM1D(activity=u'active') + TP53(activity=u'inactive'), kf_pt_act_1)
Rule(u'PPM1D_deactivates_ATM_activity', PPM1D(activity=u'active') + ATM(activity=u'active') >> PPM1D(activity=u'active') + ATM(activity=u'inactive'), kf_pa_act_1)
Rule(u'MDM2_deactivates_TP53_activity', MDM2(activity=u'active') + TP53(activity=u'active') >> MDM2(activity=u'active') + TP53(activity=u'inactive'), kf_mt_act_1)
Rule(u'HIPK2_deactivates_PPM1D_activity', HIPK2() + PPM1D(activity=u'active') >> HIPK2() + PPM1D(activity=u'inactive'), kf_hp_act_1)
Rule(u'ARF_deactivates_MDM2_activity', ARF() + MDM2(activity=u'active') >> ARF() + MDM2(activity=u'inactive'), kf_am_act_1)

Initial(PPM1D(activity=u'inactive'), PPM1D_0)
Initial(TP53(activity=u'inactive'), TP53_0)
Initial(ATM(activity=u'inactive'), ATM_0)
Initial(HIPK2(), HIPK2_0)
Initial(ARF(), ARF_0)
Initial(MDM2(activity=u'inactive'), MDM2_0)
Initial(ATM(activity=u'active'), ATMa_0)

Annotation(PPM1D, u'http://identifiers.org/hgnc/HGNC:9277', u'is')
Annotation(PPM1D, u'http://identifiers.org/uniprot/O15297', u'is')
Annotation(TP53, u'http://identifiers.org/hgnc/HGNC:11998', u'is')
Annotation(TP53, u'http://identifiers.org/uniprot/P04637', u'is')
Annotation(ATM, u'http://identifiers.org/hgnc/HGNC:795', u'is')
Annotation(ATM, u'http://identifiers.org/uniprot/Q13315', u'is')
Annotation(HIPK2, u'http://identifiers.org/uniprot/Q9H2X6', u'is')
Annotation(HIPK2, u'http://identifiers.org/hgnc/HGNC:14402', u'is')
Annotation(MDM2, u'http://identifiers.org/uniprot/Q00987', u'is')
Annotation(MDM2, u'http://identifiers.org/hgnc/HGNC:6973', u'is')
Annotation(ATM_activates_ATM_activity, u'ATM', u'rule_has_subject')
Annotation(ATM_activates_ATM_activity, u'ATM', u'rule_has_object')
Annotation(ATM_activates_TP53_activity, u'ATM', u'rule_has_subject')
Annotation(ATM_activates_TP53_activity, u'TP53', u'rule_has_object')
Annotation(TP53_activates_PPM1D_activity, u'TP53', u'rule_has_subject')
Annotation(TP53_activates_PPM1D_activity, u'PPM1D', u'rule_has_object')
Annotation(TP53_activates_MDM2_activity, u'TP53', u'rule_has_subject')
Annotation(TP53_activates_MDM2_activity, u'MDM2', u'rule_has_object')
Annotation(PPM1D_deactivates_TP53_activity, u'PPM1D', u'rule_has_subject')
Annotation(PPM1D_deactivates_TP53_activity, u'TP53', u'rule_has_object')
Annotation(PPM1D_deactivates_ATM_activity, u'PPM1D', u'rule_has_subject')
Annotation(PPM1D_deactivates_ATM_activity, u'ATM', u'rule_has_object')
Annotation(MDM2_deactivates_TP53_activity, u'MDM2', u'rule_has_subject')
Annotation(MDM2_deactivates_TP53_activity, u'TP53', u'rule_has_object')
Annotation(HIPK2_deactivates_PPM1D_activity, u'HIPK2', u'rule_has_subject')
Annotation(HIPK2_deactivates_PPM1D_activity, u'PPM1D', u'rule_has_object')
Annotation(ARF_deactivates_MDM2_activity, u'ARF', u'rule_has_subject')
Annotation(ARF_deactivates_MDM2_activity, u'MDM2', u'rule_has_object')

