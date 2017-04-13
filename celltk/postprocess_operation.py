from utils.traces import TracesController
from utils.pairwise import one_to_one_assignment
import numpy as np
from utils.traces import construct_traces_based_on_next, convert_traces_to_storage, label_traces


def gap_closing(cells, DISPLACEMENT=100, MASSTHRES=0.15, maxgap=4):
    '''
    Connect cells between non-consecutive frames if it meets criteria.
    maxgap (int): the maximum frames allowed to connect two cells.
    '''
    traces = construct_traces_based_on_next(cells)
    trhandler = TracesController(traces)

    # make sure not to have a cell as both disappered and appeared cells
    for trace in trhandler.traces[:]:
        if len(trace) < 2:
            trhandler.traces.remove(trace)
    dist = trhandler.pairwise_dist()
    massdiff = trhandler.pairwise_mass()
    framediff = trhandler.pairwise_frame()

    withinarea = dist < DISPLACEMENT
    inmass = abs(massdiff) < MASSTHRES
    inframe = (framediff > 1) * (framediff <= maxgap)
    withinarea_inframe = withinarea * inframe * inmass
    # CHECK: distance as a fine cost
    withinarea_inframe = one_to_one_assignment(withinarea_inframe, dist)

    if withinarea_inframe.any():
        disapp_idx, app_idx = np.where(withinarea_inframe)

        dis_cells = trhandler.disappeared()
        app_cells = trhandler.appeared()
        for disi, appi in zip(disapp_idx, app_idx):
            dis_cell, app_cell = dis_cells[disi], app_cells[appi]
            dis_cell.next = app_cell

            # You can simply reconstruct the trace, but here to reduce the calculation,
            # connect them explicitly.
            dis_trace = [i for i in trhandler.traces if dis_cell in i][0]
            app_trace = [i for i in trhandler.traces if app_cell in i][0]
            dis_trace.extend(trhandler.traces.pop(trhandler.traces.index(app_trace)))
    traces = label_traces(trhandler.traces)
    return convert_traces_to_storage(traces)