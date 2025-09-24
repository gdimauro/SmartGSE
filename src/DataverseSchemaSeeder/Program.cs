using Microsoft.PowerPlatform.Dataverse.Client;
using Microsoft.Xrm.Sdk;
using Microsoft.Xrm.Sdk.Messages;
using Microsoft.Xrm.Sdk.Metadata;
using Microsoft.Extensions.Configuration;

class Seeder {
  private readonly ServiceClient _svc;
  public Seeder(ServiceClient svc) => _svc = svc;

  public bool EntityExists(string logical) {
    try {
      var r = (RetrieveEntityResponse)_svc.Execute(new RetrieveEntityRequest{ LogicalName = logical, EntityFilters = EntityFilters.Entity });
      return r != null;
    } catch { return false; }
  }
  public bool AttrExists(string entity,string attr) {
    try {
      var r = (RetrieveAttributeResponse)_svc.Execute(new RetrieveAttributeRequest{ EntityLogicalName = entity, LogicalName = attr });
      return r != null;
    } catch { return false; }
  }

  public void EnsureEntity(string logical, string display, string description, string primary="esg_name") {
    if (EntityExists(logical)) { Console.WriteLine($"[=] {logical}"); return; }
    var meta = new EntityMetadata {
      SchemaName = logical,
      DisplayName = new Label(display,1033),
      Description = new Label(description,1033),
      DisplayCollectionName = new Label(display+"s",1033),
      OwnershipType = OwnershipTypes.None
    };
    var req = new CreateEntityRequest {
      Entity = meta,
      PrimaryAttribute = new StringAttributeMetadata {
        SchemaName = primary, MaxLength = 300, DisplayName = new Label("Name",1033),
        RequiredLevel = new AttributeRequiredLevelManagedProperty(AttributeRequiredLevel.ApplicationRequired)
      }
    };
    _svc.Execute(req);
    Console.WriteLine($"[+] {logical}");
  }

  public void EnsureString(string entity,string schema,string display,int max=200,bool req=false){
    if (AttrExists(entity,schema)) return;
    var a = new StringAttributeMetadata{ SchemaName=schema, MaxLength=max, DisplayName=new Label(display,1033),
      RequiredLevel=new AttributeRequiredLevelManagedProperty(req?AttributeRequiredLevel.ApplicationRequired:AttributeRequiredLevel.None) };
    _svc.Execute(new CreateAttributeRequest{ EntityName=entity, Attribute=a });
    Console.WriteLine($"   [+] {entity}.{schema} (string)");
  }
  public void EnsureInt(string entity,string schema,string display,bool req=false){
    if (AttrExists(entity,schema)) return;
    var a = new IntegerAttributeMetadata{ SchemaName=schema, DisplayName=new Label(display,1033),
      RequiredLevel=new AttributeRequiredLevelManagedProperty(req?AttributeRequiredLevel.ApplicationRequired:AttributeRequiredLevel.None) };
    _svc.Execute(new CreateAttributeRequest{ EntityName=entity, Attribute=a });
    Console.WriteLine($"   [+] {entity}.{schema} (int)");
  }
  public void EnsureDec(string entity,string schema,string display,int prec=6,bool req=false){
    if (AttrExists(entity,schema)) return;
    var a = new DecimalAttributeMetadata{ SchemaName=schema, DisplayName=new Label(display,1033),
      Precision=prec, MinValue=-1000000000, MaxValue=1000000000,
      RequiredLevel=new AttributeRequiredLevelManagedProperty(req?AttributeRequiredLevel.ApplicationRequired:AttributeRequiredLevel.None) };
    _svc.Execute(new CreateAttributeRequest{ EntityName=entity, Attribute=a });
    Console.WriteLine($"   [+] {entity}.{schema} (decimal)");
  }
  public void EnsureDate(string entity,string schema,string display,bool req=false){
    if (AttrExists(entity,schema)) return;
    var a = new DateTimeAttributeMetadata{ SchemaName=schema, DisplayName=new Label(display,1033),
      Format=DateTimeFormat.DateOnly,
      RequiredLevel=new AttributeRequiredLevelManagedProperty(req?AttributeRequiredLevel.ApplicationRequired:AttributeRequiredLevel.None) };
    _svc.Execute(new CreateAttributeRequest{ EntityName=entity, Attribute=a });
    Console.WriteLine($"   [+] {entity}.{schema} (date)");
  }
  public void EnsureLookup(string from,string schema,string display,string to,string relName){
    if (AttrExists(from,schema)) return;
    var req = new CreateOneToManyRequest {
      OneToManyRelationship = new OneToManyRelationshipMetadata{
        ReferencedEntity = to, ReferencingEntity = from, SchemaName = relName,
        CascadeConfiguration = new CascadeConfiguration{ Delete = CascadeType.Restrict }
      },
      Lookup = new LookupAttributeMetadata{
        SchemaName = schema, DisplayName = new Label(display,1033),
        RequiredLevel = new AttributeRequiredLevelManagedProperty(AttributeRequiredLevel.None)
      }
    };
    _svc.Execute(req);
    Console.WriteLine($"   [+] {from}.{schema} (lookup→{to})");
  }
}

class Program {
  static int Main(string[] args){
    var cfg = new ConfigurationBuilder()
      .AddJsonFile("appsettings.json", optional:false)
      .AddEnvironmentVariables()
      .Build();
    var url = cfg["Url"]; var clientId = cfg["ClientId"]; var secret = cfg["ClientSecret"]; var tenant = cfg["TenantId"];
    if (string.IsNullOrWhiteSpace(url)||string.IsNullOrWhiteSpace(clientId)||string.IsNullOrWhiteSpace(secret)||string.IsNullOrWhiteSpace(tenant)){
      Console.Error.WriteLine("Missing Url/ClientId/ClientSecret/TenantId in appsettings.json"); return 1;
    }
    var conn = $"AuthType=ClientSecret;Url={url};ClientId={clientId};ClientSecret={secret};TenantId={tenant};RequireNewInstance=true;";
    using var svc = new ServiceClient(conn);
    if(!svc.IsReady){ Console.Error.WriteLine("Failed to connect to Dataverse."); return 2; }
    var s = new Seeder(svc);

    // Core tables
    s.EnsureEntity("esg_organization","Organization","Reporting organization");
    s.EnsureString("esg_organization","esg_countryiso","Country ISO",4);
    s.EnsureString("esg_organization","esg_sectornace","Sector (NACE)",50);

    s.EnsureEntity("esg_legalentity","Legal Entity","Legal entity");
    s.EnsureLookup("esg_legalentity","esg_organizationid","Organization","esg_organization","esg_organization_legalentities");
    s.EnsureString("esg_legalentity","esg_vat","VAT",50);

    s.EnsureEntity("esg_site","Site","Physical site");
    s.EnsureLookup("esg_site","esg_legalentityid","Legal Entity","esg_legalentity","esg_legalentity_sites");
    s.EnsureString("esg_site","esg_type","Type",20);
    s.EnsureDec("esg_site","esg_geolat","Latitude");
    s.EnsureDec("esg_site","esg_geolon","Longitude");

    s.EnsureEntity("esg_reportingperiod","Reporting Period","Fiscal/reporting period");
    s.EnsureInt("esg_reportingperiod","esg_fiscalyear","Fiscal Year", true);
    s.EnsureDate("esg_reportingperiod","esg_startdate","Start Date", true);
    s.EnsureDate("esg_reportingperiod","esg_enddate","End Date", true);
    s.EnsureString("esg_reportingperiod","esg_status","Status",20);
    s.EnsureString("esg_reportingperiod","esg_currency","Currency",10);

    s.EnsureEntity("esg_unit","Unit","Measurement unit");
    s.EnsureEntity("esg_gwpfactor","GWP Factor","Global warming potentials");
    s.EnsureEntity("esg_scope3category","Scope3 Category","GHG Protocol Scope 3");
    s.EnsureEntity("esg_esrsdatapoint","ESRS Datapoint","ESRS datapoint");

    s.EnsureEntity("esg_supplier","Supplier","Supplier master");
    s.EnsureEntity("esg_customer","Customer","Customer master");

    s.EnsureEntity("esg_activity","Activity","Activity data");
    s.EnsureLookup("esg_activity","esg_periodid","Reporting Period","esg_reportingperiod","esg_period_activities");
    s.EnsureLookup("esg_activity","esg_siteid","Site","esg_site","esg_site_activities");
    s.EnsureString("esg_activity","esg_scope","Scope",10);
    s.EnsureString("esg_activity","esg_activitytype","Activity Type",100);
    s.EnsureDec("esg_activity","esg_quantity","Quantity");
    s.EnsureString("esg_activity","esg_unit","Unit",20);

    s.EnsureEntity("esg_activitydetail_electricity","Activity Electricity","Electricity details");
    s.EnsureLookup("esg_activitydetail_electricity","esg_activityid","Activity","esg_activity","esg_activity_electricitydetails");
    s.EnsureString("esg_activitydetail_electricity","esg_marketmethod","Market Method",20);
    s.EnsureDec("esg_activitydetail_electricity","esg_kwh","kWh");

    s.EnsureEntity("esg_emissionfactor","Emission Factor","Emission factors");
    s.EnsureEntity("esg_factorset","Factor Set","Factor set");
    s.EnsureEntity("esg_calcmodel","Calculation Model","Calculation model");
    s.EnsureEntity("esg_calcrun","Calculation Run","Calculation run");
    s.EnsureLookup("esg_calcrun","esg_periodid","Reporting Period","esg_reportingperiod","esg_period_calcruns");
    s.EnsureLookup("esg_calcrun","esg_modelid","Calculation Model","esg_calcmodel","esg_model_calcruns");

    s.EnsureEntity("esg_emission","Emission","Emission result");
    s.EnsureLookup("esg_emission","esg_activityid","Activity","esg_activity","esg_activity_emissions");
    s.EnsureLookup("esg_emission","esg_modelid","Calculation Model","esg_calcmodel","esg_model_emissions");
    s.EnsureString("esg_emission","esg_gas","Gas",20);
    s.EnsureDec("esg_emission","esg_amount","Amount");
    s.EnsureDec("esg_emission","esg_co2e","CO2e");

    s.EnsureEntity("esg_emissionagg","Emission Aggregate","Aggregated emissions");
    s.EnsureLookup("esg_emissionagg","esg_periodid","Reporting Period","esg_reportingperiod","esg_period_emissionaggs");

    s.EnsureEntity("esg_energycertificate","Energy Certificate","GO/REC");
    s.EnsureEntity("esg_energycontract","Energy Contract","Energy contract");

    s.EnsureEntity("esg_target","Target","Climate/ESG Target");
    s.EnsureEntity("esg_initiative","Initiative","Project/Initiative");
    s.EnsureLookup("esg_initiative","esg_targetid","Target","esg_target","esg_target_initiatives");

    s.EnsureEntity("esg_datasource","Data Source","ETL data source");
    s.EnsureEntity("esg_ingestionjob","Ingestion Job","ETL job");
    s.EnsureLookup("esg_ingestionjob","esg_datasourceid","Data Source","esg_datasource","esg_datasource_jobs");
    s.EnsureEntity("esg_transformation","Transformation","ETL transformation");
    s.EnsureLookup("esg_transformation","esg_jobid","Job","esg_ingestionjob","esg_job_transformations");

    s.EnsureEntity("esg_dqrule","Data Quality Rule","DQ rule");
    s.EnsureEntity("esg_approval","Approval","Period approval");
    s.EnsureLookup("esg_approval","esg_periodid","Reporting Period","esg_reportingperiod","esg_period_approvals");
    s.EnsureEntity("esg_evidence","Evidence","Evidence");
    s.EnsureEntity("esg_lock","Lock","Period lock");
    s.EnsureLookup("esg_lock","esg_periodid","Reporting Period","esg_reportingperiod","esg_period_locks");

    s.EnsureEntity("esg_disclosure","Disclosure","Framework disclosure");
    s.EnsureEntity("esg_disclosurereq","Disclosure Requirement","Requirement");
    s.EnsureLookup("esg_disclosurereq","esg_disclosureid","Disclosure","esg_disclosure","esg_disclosure_requirements");

    Console.WriteLine("\nSchema seeding completed.");
    return 0;
  }
}
