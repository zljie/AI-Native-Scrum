const fs=require('node:fs');
const path=require('node:path');
// Emit success evidence only after actual browser execution, never from test listing.
class ContractReporter {
 onBegin(config,suite){this.suite=suite;this.config=config;}
 onEnd(result){
  const output=path.resolve('test-results/contract-result.json');
  fs.mkdirSync(path.dirname(output),{recursive:true});
  const tests=this.suite.allTests();
  const skipped=tests.filter(t=>t.results.length===0||t.results.some(r=>r.status==='skipped')).length;
  const passed=tests.filter(t=>t.results.length===1&&t.results[0].status==='passed').length;
  const valid=result.status==='passed'&&tests.length>=9&&passed===tests.length&&skipped===0;
  const report={pageIds:['demo-list'],status:valid?'passed':'failed',exitCode:valid?0:1,testsPassed:passed,testsSkipped:skipped,
   testsTotal:tests.length,browser:'chromium',viewport:{width:1280,height:800},additionalViewports:[{width:390,height:844}],
   command:'npm test',completedAt:new Date().toISOString(),checks:valid?['layout','tail-columns','search-behavior','pagination-behavior']:[],
   tests:tests.map(t=>({title:t.title,status:t.results.at(-1)?.status??'not-run'}))};
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
 }
}
module.exports=ContractReporter;
