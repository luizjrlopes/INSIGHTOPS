export type Session={token:string;user:{id:string;name:string;role:string}};
export type KPI={metric:string;display_value:string;numeric_value:number;change:string;kind:string};
export type Anomaly={id:string;metric:string;scope:string;severity:string;score:number;delta:string;status:string;resolution_note?:string|null;evidence?:{label:string;value:string;source:string}[]};
