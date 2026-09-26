from pathlib import Path
import json,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
O=Path(__file__).resolve().parent;d=json.loads((O/'data_summary.json').read_text())
# The archived summary retains the historical 457-question synthetic frame.
# Apply the source-conflict exclusion before regenerating manuscript tables.
correction=json.loads((O/'interest_sensitivity.json').read_text())['scenarios']['exclude_direct_2']['readers']
for row in d['settings']:
 if row['setting'] not in ('Synthetic / DeepSeek','Synthetic / GPT6'):continue
 fixed=correction[row['setting'].split(' / ')[1]];n=fixed['n']
 row.update(n=n,failure=fixed['bare_errors']/n,definition_accuracy=1-fixed['definition_errors']/n,
            risk_auc=fixed['table3_R_auc'],pd_auc=fixed['table3_dp_auc'],risk_ci=fixed['table3_R_ci'],
            risk_repair_auc=fixed['appendix_R_unconditional_repair_auc'],
            pd_repair_auc=fixed['appendix_dp_unconditional_repair_auc'],
            pd_minus_risk_ci=fixed['appendix_dp_minus_R_error_ci'])
def display_setting(name):
 reader='DeepSeek V4 Flash' if name.startswith('Synthetic / DeepSeek') else 'DeepSeek V4.1 Flash'
 return name.replace('DeepSeek',reader).replace('GPT6','GPT-6-astra').replace('GPT5.6','GPT-5.6-terra')
def tab(path,caption,label,fmt,head,rows,size='small'):
 s=['\\begin{table}[t]\\centering\\'+size,r'\caption{'+caption+'}',r'\label{'+label+'}',r'\begin{tabular}{@{}'+fmt+r'@{}}\toprule',head+r'\\\midrule']
 s += [row+chr(92)*2 for row in rows];s += [r'\bottomrule\end{tabular}\end{table}'];(O/path).write_text('\n'.join(s))
rows=[]
for r in d['settings']:
 corpus,reader=display_setting(r['setting']).split(' / ');lo,hi=r['risk_ci']
 rows.append(f"{corpus.replace(' library','')} & {reader} & {r['n']:,} & {r['failure']:.3f} & {1-r['definition_accuracy']:.3f} & {r['risk_auc']:.3f} [{lo:.3f}, {hi:.3f}] & {r['pd_auc']:.3f}")
tab('section/table_prediction.tex',r'Reader error without and with the definition text, and AUROC of proxy scores for ranking bare errors. The definition text is a model-drafted source-based gloss for synthetic, Reddit, and DeFi, and extracted contract wording for CUAD. Rows differ in reader and question construction (Appendix~\ref{app:setting-design}). CUAD is risk-stratified.', 'tab:prediction','llrcccc',r'Corpus & Reader & $n$ & Error, no def. & Error, def. & $R$ AUROC [95\% CI] & $\Delta p$ AUROC',rows,r'footnotesize\setlength{\tabcolsep}{4pt}')
rows=[]
for r in d['rag']:
 if r['tier']!='hybrid' or not (r['corpus']=='CUAD' or r['subset'] in ['glossary','all','control']):continue
 v=r['accuracy'];name=r['corpus']+(' / '+r['subset'] if r['corpus']=='Reddit' else '')
 matched=f"{v['rag_defrecall']:.3f}" if 'rag_defrecall' in v else '--'
 rows.append(f"{name} & {r['n']:,} & {v['rag']:.3f} & {v['rag_gated']:.3f} & {matched} & {v['rag_full']:.3f}")
tab('appendix/table_selection.tex',r'In-sample hybrid-retrieval results on constructed questions. The risk aggregate includes the evaluated diagnostic item. The all-matched arm is unavailable for Reddit; the CUAD full glossary is capped at 30 entries. These arms are not matched-budget random or frequency policies.','tab:selection','lrcccc',r'Workload & $n$ & Retrieval & Selected notes & All matched & Full glossary',rows)
rows=[]
for r in d['settings']:
 lo,hi=r['pd_minus_risk_ci'];rows.append(f"{display_setting(r['setting'])} & {r['n']} & {r['risk_repair_auc']:.3f} & {r['pd_repair_auc']:.3f} & [{lo:.3f}, {hi:.3f}]")
tab('appendix/table_repair.tex',r'Prediction of observed repair. The last column concerns the separate bare-error target and gives a paired ranking difference. $R$ and $\Delta p$ are algebraically coupled (Appendix~\ref{app:coupling}).','tab:repair','p{4.5cm}rccc',r'Setting & $n$ & $R$, repair AUC & $\Delta p$, repair AUC & Error AUC difference CI',rows,'footnotesize')
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':8,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False,'pdf.fonttype':42})
fig,axes=plt.subplots(1,2,figsize=(5.1,1.8),gridspec_kw={'width_ratios':[1.1,1]},layout='constrained')
a=axes[0];x=np.arange(.1,1,.2);y=[r['failure'] for r in d['weighted_cuad']['bins']];a.plot([0,1],[0,1],':',c='#92999F',lw=.8);a.plot(x,y,'o-',c='#335C81',lw=1.3,ms=3);a.set_xlim(0,1);a.set_ylim(0,1);a.set_xlabel('Proxy risk bin centre');a.set_ylabel('Observed reader error');a.text(0,1.05,'a',transform=a.transAxes,fontweight='bold')
a=axes[1];labels=['Correct in both','Repaired','Still wrong','Harmed'];counts=[1097,163,157,83];colors=['#92999F','#335C81','#92999F','#B4674D'];yy=np.arange(4);a.barh(yy,counts,color=colors,height=.55);a.set_yticks(yy,labels);a.invert_yaxis();a.set_xlim(0,1270);a.set_xlabel('Number of questions');a.text(0,1.05,'b',transform=a.transAxes,fontweight='bold')
for i,n in enumerate(counts):a.text(n+25,i,str(n),va='center',fontsize=7)
fig.savefig(O/'figs/stratification.pdf',bbox_inches='tight',pad_inches=.03);fig.savefig(O/'figs/stratification.png',dpi=220,bbox_inches='tight',pad_inches=.03)
plt.close(fig)
