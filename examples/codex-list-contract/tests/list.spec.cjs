const {test,expect}=require('@playwright/test');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const url=pathToFileURL(path.resolve(__dirname,'../index.html')).href;

// Reusable DOM adapter. Production routes need their own field/data adapter and behavior tests.
async function inspectContract(page){
 return page.evaluate(()=>{
  const errors=[];
  function visible(selector,id){
   const nodes=document.querySelectorAll(selector);
   if(nodes.length!==1){errors.push(`${id}:missing-or-duplicate`);return null;}
   const element=nodes[0],rect=element.getBoundingClientRect(),style=getComputedStyle(element);
   if(!rect.width||!rect.height||style.display==='none'||style.visibility==='hidden'||Number(style.opacity)===0){errors.push(`${id}:not-visible`);return null;}
   return rect;
  }
  const search=visible('[data-contract="search"]','search'),table=visible('[data-contract="table"]','table'),pagination=visible('[data-contract="pagination"]','pagination');
  if(search&&table&&search.bottom>table.top)errors.push('UI-LIST-001');
  if(pagination&&table&&pagination.top<table.bottom)errors.push('UI-LIST-002');
  const nodes=Array.from(document.querySelectorAll('thead th'));
  if(nodes.some(n=>{const r=n.getBoundingClientRect(),s=getComputedStyle(n);return !r.width||!r.height||s.visibility==='hidden'||s.display==='none'||Number(s.opacity)===0;}))errors.push('UI-LIST-003:hidden-header');
  const headers=nodes.map(n=>n.textContent.trim());
  if(JSON.stringify(headers.slice(-3))!==JSON.stringify(['创建人','最后更新时间','操作']))errors.push('UI-LIST-003');
  return errors;
 });
}
test.beforeEach(async({page})=>{await page.goto(url);});
test('valid list: visible ordered regions and exact final three columns',async({page})=>{
 expect(await inspectContract(page)).toEqual([]);
 await expect(page.getByRole('columnheader')).toHaveText(['报告名称','创建人','最后更新时间','操作']);
});
test('search changes results, resets page; pagination changes displayed records',async({page})=>{
 await expect(page.locator('tbody tr')).toHaveCount(5);
 await page.getByRole('button',{name:'下一页',exact:true}).click();
 await expect(page.locator('tbody tr').first()).toContainText('模拟报告 6');
 await page.getByRole('searchbox').fill('12');
 await page.getByRole('button',{name:'搜索',exact:true}).click();
 await expect(page.locator('tbody tr')).toHaveCount(1);
 await expect(page.locator('tbody tr')).toContainText('模拟报告 12');
 await expect(page.locator('#page')).toHaveText('第 1 / 1 页 · 共 1 条');
 await expect(page.getByRole('button',{name:'下一页',exact:true})).toBeDisabled();
 await page.getByRole('button',{name:'查看模拟报告 12',exact:true}).click();
 await expect(page.locator('#detail')).toHaveText('当前查看：模拟报告 12');
});
test('empty results preserve layout and pagination',async({page})=>{
 await page.getByRole('searchbox').fill('不存在');await page.getByRole('button',{name:'搜索',exact:true}).click();
 await expect(page.locator('tbody')).toHaveText('暂无结果');expect(await inspectContract(page)).toEqual([]);
});
test('narrow viewport preserves vertical layout and horizontally scrollable table',async({page})=>{
 await page.setViewportSize({width:390,height:844});expect(await inspectContract(page)).toEqual([]);
 expect(await page.locator('.table-wrap').evaluate(e=>e.scrollWidth>e.clientWidth)).toBe(true);
});
const mutations={
 'search below table':{rule:'UI-LIST-001',code:()=>document.querySelector('[data-contract="table"]').after(document.querySelector('[data-contract="search"]'))},
 'pagination above table':{rule:'UI-LIST-002',code:()=>document.querySelector('[data-contract="table"]').before(document.querySelector('[data-contract="pagination"]'))},
 'audit columns swapped':{rule:'UI-LIST-003',code:()=>{const h=document.querySelectorAll('th');h[1].before(h[2]);}},
 'updated time omitted':{rule:'UI-LIST-003',code:()=>document.querySelectorAll('th')[2].remove()}
};
for(const [name,{rule,code}] of Object.entries(mutations))test(`negative contract: ${name} is rejected`,async({page})=>{
 await page.evaluate(code);expect(await inspectContract(page)).toContain(rule);
});
test('missing page regions fail closed',async({page})=>{
 await page.locator('main').evaluate(e=>e.remove());
 expect(await inspectContract(page)).toEqual(expect.arrayContaining(['search:missing-or-duplicate','table:missing-or-duplicate','pagination:missing-or-duplicate','UI-LIST-003']));
});
