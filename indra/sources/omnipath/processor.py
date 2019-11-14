from __future__ import unicode_literals
import logging
from collections import Counter
from indra.preassembler.grounding_mapper import GroundingMapper
from indra.statements import modtype_to_modclass, Agent, Evidence, Complex

logger = logging.getLogger(__file__)

try:
    from pypath.intera import Complex as pp_Complex
    has_pypath = True
except ImportError:
    has_pypath = False
    pp_Complex = None


class OmniPathBaseProcessor(object):
    def __init__(self):
        self.statements = []

    def _agent_from_up_id(self, up_id):
        """Build an Agent object from a Uniprot ID. Adds db_refs for both
        Uniprot and HGNC where available."""
        db_refs = {'UP': up_id}
        ag = Agent(None, db_refs=db_refs)
        GroundingMapper.standardize_agent_name(ag)
        return ag

    def _complex_agents_from_op_complex(self, up_id_string):
        """Return a list of agents from a string containing multiple UP ids
        """
        # Return list of contained agents
        if 'COMPLEX' in up_id_string:
            if ' ' in up_id_string:
                up_id_string = up_id_string.split()[-1]
            return [self._agent_from_up_id(up_id) for up_id in
                    up_id_string.split('COMPLEX:')[1].split('_')]
        else:
            return [self._agent_from_up_id(up_id_string)]


class OmniPathModificationProcessor(OmniPathBaseProcessor):
    def __init__(self, ptm_json=None):
        super().__init__()
        self.statements.extend(self._stmts_from_op_mods(ptm_json))

    def _stmts_from_op_mods(self, ptm_json):
        """Build Modification Statements from a list of Omnipath PTM entries
        """
        ptm_stmts = []
        unhandled_mod_types = []
        if ptm_json is None:
            return []
        for mod_entry in ptm_json:
            enz = self._agent_from_up_id(mod_entry['enzyme'])
            sub = self._agent_from_up_id(mod_entry['substrate'])
            res = mod_entry['residue_type']
            pos = mod_entry['residue_offset']
            #evidence = [Evidence('omnipath', None, pmid)
            #            for pmid in mod_entry['references']]
            evidence = [Evidence('omnipath', None, None)]
            mod_type = mod_entry['modification']
            modclass = modtype_to_modclass.get(mod_type)
            if modclass is None:
                unhandled_mod_types.append(mod_type)
                continue
            else:
                stmt = modclass(enz, sub, res, pos, evidence)
            ptm_stmts.append(stmt)
        print(Counter(unhandled_mod_types))
        return ptm_stmts


class OmniPathLiganReceptorProcessor(OmniPathBaseProcessor):
    def __init__(self, pa):
        """Process ligand-receptor interactions from PyPath

        Parameters
        ----------
        pa : pypath.main.PyPath
            An instance of a PyPath object containing the network
            representing ligand-receptor interactions
        """
        super().__init__()
        self.pa = pa
        self.statements.extend(self._stmts_from_op_pypath_graph(self.pa))

    @staticmethod
    def _get_text_refs(article_id_list):
        text_refs = {}
        for ref in article_id_list:
            name = ref['idtype'].upper()
            try:
                id = int(ref['value'])
            except ValueError:
                id = ref['value']
            text_refs[name] = id
        return text_refs

    @staticmethod
    def _get_annotations(ref_info):
        """ref_info is a dict returned by the method 'info' of a
        pypath.refs.Reference object"""
        annotations = {}
        uid = ref_info['uids'][0]
        ref_dict = ref_info[uid]
        if ref_dict.get('recordstatus'):
            annotations['recordstatus'] = ref_dict['recordstatus']
        if ref_dict.get('pubstatus'):
            annotations['pubstatus'] = ref_dict['pubstatus']
        if ref_dict.get('pmcrefcount'):
            annotations['pmcrefcount'] = ref_dict['pmcrefcount']
        if ref_dict.get('reportnumber'):
            annotations['reportnumber'] = ref_dict['reportnumber']
        if ref_dict.get('availablefromurl'):
            annotations['availablefromurl'] = ref_dict['availablefromurl']
        if ref_dict.get('locationlabel'):
            annotations['locationlabel'] = ref_dict['locationlabel']
        return annotations

    def _stmts_from_op_pypath_graph(self, pa):
        """Build Complex statements from an igraph of ligand-receptor
        interactions

        Parameters
        ----------
        pa : pypath.main.PyPath
            An instance of a PyPath object containing the network
            representing ligand-receptor interactions
        """
        stmt_list = []
        for s, t in pa.graph.get_edgelist():
            edge_obj = pa.get_edge(s, t)

            # Get participating agents
            if isinstance(pa.vs[s]['name'], pp_Complex):
                # Catch the odd pypath.intera.Complex objects
                src_string = str(pa.vs[s]['name'])
            else:
                src_string = pa.vs[s]['name']
            source_agents = self._complex_agents_from_op_complex(src_string)

            if isinstance(pa.vs[t]['name'], pp_Complex):
                # Catch the odd pypath.intera.Complex objects
                trg_string = str(pa.vs[t]['name'])
            else:
                trg_string = pa.vs[t]['name']
            target_agents = self._complex_agents_from_op_complex(trg_string)

            # Assemble agent list
            agent_list = []
            for agent in [*source_agents, *target_agents]:
                if agent not in agent_list:
                    agent_list.append(agent)

            # Get article IDs by support
            for ref_name, ref_set in edge_obj['refs_by_source'].items():
                for ref_obj in ref_set:
                    # Ref obj is a pypath.refs.Reference object
                    # Check for PMID
                    if ref_obj.pmid:
                        pmid = ref_obj.pmid
                    else:
                        pmid = None
                    try:
                        # pypath.refs.Reference.info() returns a dictionary
                        # of reference info. If load fails silently, an
                        # empty dict is returned.
                        ref_info = ref_obj.info()
                        if ref_info.get('uids'):
                            uid = ref_info['uids'][0]
                            # Text refs
                            text_refs = self._get_text_refs(
                                ref_info[uid]['articleids'])
                            text_refs['nlmuniqueid'] =\
                                ref_info[uid]['nlmuniqueid']
                            text_refs['ISSN'] = ref_info[uid]['issn']
                            text_refs['ESSN'] = ref_info[uid]['essn']
                        else:
                            text_refs = None
                    except TypeError as e:
                        logger.warning('Failed to load info')
                        logger.exception(e)
                        ref_info = None
                        text_refs = None

                    # If both pmid and text_refs is None, skip this Complex
                    if pmid is None and text_refs is None:
                        logger.info('Skipping statement for %s' % ref_name)
                        continue

                    # Get annotations
                    if ref_info:
                        annotations = self._get_annotations(ref_info)
                        annotations['source_sub_id'] = ref_name
                    else:
                        annotations = {'source_sub_id': ref_name}
                    if ref_name == 'Ramilowski2015' and\
                            edge_obj['ramilowski_sources']:
                        annotations['ramilowski_sources'] =\
                            edge_obj['ramilowski_sources']
                    if ref_name.lower() == 'cellphonedb' and\
                            edge_obj['cellphonedb_type']:
                        annotations['cellphonedb_type'] =\
                            edge_obj['cellphonedb_type']
                    evidence = Evidence('omnipath', None, pmid,
                                        annotations=annotations,
                                        text_refs=text_refs)
                    stmt_list.append(Complex(agent_list, evidence))

        return stmt_list
