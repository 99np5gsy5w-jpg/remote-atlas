export const MONTHLY_PRICE = 14.99;
export const ANNUAL_PRICE = 119.99;
export type Channel = 'ios15' | 'ios30' | 'web';
export type Billing = 'monthly' | 'annual' | 'mixed';
export function costs({users=1000,minutes=90,maintenance=16,iosHours=6,channel='ios15',billing='monthly',privateRunner=false}:{users?:number;minutes?:number;maintenance?:number;iosHours?:number;channel?:Channel;billing?:Billing;privateRunner?:boolean}={}) {
 const ios=channel!=='web', rate=channel==='ios15'?.15:.30;
 const crawl=privateRunner?Math.max(0,minutes*30-2000)*.006:0;
 const infrastructure=112+crawl, coreLabor=maintenance*75, iosLabor=ios?iosHours*75:0, apple=ios?99/12:0;
 const fixed=infrastructure+coreLabor+iosLabor+apple, variable=users*.1;
 const monthlyFee=ios?MONTHLY_PRICE*rate:MONTHLY_PRICE*.036+.30;
 const annualFee=(ios?ANNUAL_PRICE*rate:ANNUAL_PRICE*.036+.30)/12;
 const monthlyShare=billing==='monthly'?1:billing==='annual'?0:.5;
 const revenuePerUser=monthlyShare*MONTHLY_PRICE+(1-monthlyShare)*ANNUAL_PRICE/12;
 const feePerUser=monthlyShare*monthlyFee+(1-monthlyShare)*annualFee;
 const contribution=revenuePerUser-feePerUser-.1, fees=users*feePerUser;
 return {crawl,infrastructure,coreLabor,iosLabor,apple,fixed,variable,fees,monthlyFee,annualFee,contribution,revenue:users*revenuePerUser,total:fixed+variable+fees,breakEven:Math.ceil(fixed/contribution)};
}
