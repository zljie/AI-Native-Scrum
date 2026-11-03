const {defineConfig}=require('@playwright/test');
module.exports=defineConfig({
 testDir:'./tests',fullyParallel:false,workers:1,forbidOnly:!!process.env.CI,retries:0,
 reporter:[['list'],['./contract-reporter.cjs'],['json',{outputFile:'test-results/results.json'}]],
 use:{browserName:'chromium',headless:true,viewport:{width:1280,height:800},trace:'retain-on-failure',screenshot:'only-on-failure',
 launchOptions:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE?{executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE}:{}}
});
