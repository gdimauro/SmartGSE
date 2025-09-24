using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

record Attr(string name, string dataType, bool required=false);
record Ent(string name, List<Attr> attributes);
record Rel(string name, string fromEntity, string fromAttribute, string toEntity, string toAttribute);

class Program {
  static void Main() {
    var root = Path.Combine(Directory.GetCurrentDirectory(), "CDM", "BilancioESG");
    var entDir = Path.Combine(root, "entities");
    Directory.CreateDirectory(entDir);

    // --- entity schema (core set) ---
    List<Ent> entities = new() {
      E("Organization", A(("id","guid",true),("name","string",true),("countryIso","string",false),("sectorNace","string",false),("esrsReportingScope","string",false),("consolidationMethod","string",false),("createdOn","datetime",false),("modifiedOn","datetime",false))),
      E("LegalEntity", A(("id","guid",true),("organizationId","guid",true),("name","string",true),("vat","string",false),("countryIso","string",false),("createdOn","datetime",false),("modifiedOn","datetime",false))),
      E("Site", A(("id","guid",true),("legalEntityId","guid",true),("name","string",true),("type","string",true),("geoLat","number",false),("geoLon","number",false),("gridRegion","string",false),("waterBasinCode","string",false),("biodiversitySensitivityClass","string",false),("createdOn","datetime",false),("modifiedOn","datetime",false))),
      E("ReportingPeriod", A(("id","guid",true),("fiscalYear","int64",true),("startDate","date",true),("endDate","date",true),("status","string",true),("currency","string",true),("createdOn","datetime",false),("modifiedOn","datetime",false))),
      E("Unit", A(("code","string",true),("description","string",false),("unitType","string",false))),
      E("GwpFactor", A(("id","guid",true),("source","string",true),("gas","string",true),("horizon","string",true),("factor","number",true),("validFrom","date",false),("validTo","date",false))),
      E("Scope3Category", A(("code","string",true),("name","string",true),("description","string",false))),
      E("EsrsDatapoint", A(("code","string",true),("title","string",true),("esrsStandard","string",true),("dataType","string",true),("isMandatory","boolean",false),("xbrlTag","string",false))),
      E("Supplier", A(("id","guid",true),("name","string",true),("taxId","string",false),("countryIso","string",false),("sector","string",false),("esgRating","string",false))),
      E("Customer", A(("id","guid",true),("name","string",true),("countryIso","string",false),("sector","string",false))),
      E("Asset", A(("id","guid",true),("siteId","guid",true),("category","string",true),("manufacturer","string",false),("model","string",false),("serial","string",false),("lifeStart","date",false),("lifeEnd","date",false))),
      E("Meter", A(("id","guid",true),("siteId","guid",true),("type","string",true),("unit","string",true),("providerId","guid",false),("calibrationDueOn","date",false))),
      E("Activity", A(("id","guid",true),("periodId","guid",true),("legalEntityId","guid",false),("siteId","guid",false),("businessUnitId","guid",false),("scope","string",true),("activityType","string",true),("quantity","number",true),("unit","string",true),("dataQuality","string",false),("sourceSystem","string",false),("evidenceId","guid",false),("activityDate","date",false),("description","string",false))),
      E("ActivityDetail_Electricity", A(("activityId","guid",true),("marketMethod","string",true),("gridRegion","string",false),("contractId","guid",false),("meterId","guid",false),("kWh","number",true),("renewableSharePct","number",false))),
      E("EmissionFactor", A(("id","guid",true),("source","string",true),("category","string",true),("region","string",false),("year","int64",false),("gas","string",true),("unitInput","string",true),("unitOutput","string",true),("value","number",true),("validFrom","date",false),("validTo","date",false),("uncertaintyPct","number",false))),
      E("EstimationFactor", A(("id","guid",true),("method","string",true),("forActivityType","string",true),("value","number",true),("logic","string",false))),
      E("FactorSet", A(("id","guid",true),("name","string",true),("year","int64",false),("priorityOrder","int64",false),("notes","string",false))),
      E("CalculationModel", A(("id","guid",true),("name","string",true),("version","string",true),("description","string",false),("rulesJson","string",false),("factorsetId","guid",false),("gwpSet","string",false))),
      E("CalculationRun", A(("id","guid",true),("periodId","guid",true),("modelId","guid",true),("startedOn","datetime",true),("finishedOn","datetime",false),("status","string",true),("byUser","string",false),("logRef","string",false))),
      E("Emission", A(("id","guid",true),("activityId","guid",true),("modelId","guid",true),("scope","string",true),("gas","string",true),("amount","number",true),("unit","string",true),("co2e","number",true),("method","string",true),("notes","string",false))),
      E("EmissionAggregate", A(("id","guid",true),("periodId","guid",true),("legalEntityId","guid",false),("siteId","guid",false),("scope","string",true),("category","string",false),("gas","string",true),("co2e","number",true),("normalizationBasis","string",false),("intensity","number",false))),
      E("EnergyCertificate", A(("id","guid",true),("type","string",true),("periodId","guid",true),("siteId","guid",true),("volumeMWh","number",true),("vintage","int64",false),("supplierId","guid",false),("serialRange","string",false),("retiredOn","date",false),("allocationNote","string",false))),
      E("EnergyContract", A(("id","guid",true),("siteId","guid",true),("supplierId","guid",false),("productType","string",true),("startDate","date",true),("endDate","date",false),("termsJson","string",false))),
      E("Target", A(("id","guid",true),("topic","string",true),("baseYear","int64",false),("targetYear","int64",true),("scope","string",false),("absoluteOrIntensity","string",true),("value","number",true),("unit","string",true),("sbtiValidated","boolean",false))),
      E("Initiative", A(("id","guid",true),("targetId","guid",true),("type","string",true),("start","date",true),("end","date",false),("owner","string",false),("expectedCO2eReduction","number",false),("capex","number",false),("opex","number",false),("npv","number",false),("status","string",false))),
      E("DataSource", A(("id","guid",true),("name","string",true),("type","string",true),("owner","string",false))),
      E("IngestionJob", A(("id","guid",true),("dataSourceId","guid",true),("schedule","string",false),("lastRun","datetime",false),("rowsIn","int64",false),("rowsOK","int64",false),("dqIssues","int64",false))),
      E("Transformation", A(("id","guid",true),("jobId","guid",true),("mapJson","string",true),("version","string",false))),
      E("DataQualityRule", A(("id","guid",true),("name","string",true),("ruleType","string",true),("expression","string",true),("severity","string",true),("autoFix","boolean",false))),
      E("Approval", A(("id","guid",true),("periodId","guid",true),("approver","string",true),("date","date",true),("scope","string",false),("comment","string",false))),
      E("Evidence", A(("id","guid",true),("fileRef","string",true),("sha256","string",true),("collectedOn","datetime",true),("collectedBy","string",false),("linkedTo","string",false))),
      E("Lock", A(("id","guid",true),("periodId","guid",true),("lockedOn","datetime",true),("lockedBy","string",true),("checksum","string",false))),
      E("Disclosure", A(("code","string",true),("title","string",true),("framework","string",true))),
      E("DisclosureRequirement", A(("id","guid",true),("disclosureId","guid",true),("datapointCode","string",true),("calculation","string",false),("sourceEntities","string",false),("xbrlTag","string",false),("materialityDependency","string",false))),
      E("ReportTable", A(("id","guid",true),("name","string",true),("layoutJson","string",true),("ordering","int64",false),("notes","string",false)))
    };

    List<Rel> rels = new() {
      R("LegalEntity_Organization","LegalEntity","organizationId","Organization","id"),
      R("Site_LegalEntity","Site","legalEntityId","LegalEntity","id"),
      R("Asset_Site","Asset","siteId","Site","id"),
      R("Meter_Site","Meter","siteId","Site","id"),
      R("Activity_Period","Activity","periodId","ReportingPeriod","id"),
      R("Activity_Site","Activity","siteId","Site","id"),
      R("CalcRun_Model","CalculationRun","modelId","CalculationModel","id"),
      R("Emission_Activity","Emission","activityId","Activity","id"),
      R("Emission_Model","Emission","modelId","CalculationModel","id"),
      R("EmissionAgg_Period","EmissionAggregate","periodId","ReportingPeriod","id"),
      R("EnergyCert_Site","EnergyCertificate","siteId","Site","id"),
      R("EnergyCert_Period","EnergyCertificate","periodId","ReportingPeriod","id"),
      R("Initiative_Target","Initiative","targetId","Target","id"),
      R("Approval_Period","Approval","periodId","ReportingPeriod","id"),
      R("Lock_Period","Lock","periodId","ReportingPeriod","id"),
      R("IngestionJob_DataSource","IngestionJob","dataSourceId","DataSource","id"),
      R("Transformation_Job","Transformation","jobId","IngestionJob","id")
    };

    // write empty CSVs + headers
    foreach (var e in entities) {
      var csv = Path.Combine(entDir, e.name + ".csv");
      using var sw = new StreamWriter(csv);
      sw.WriteLine(string.Join(",", e.attributes.Select(a => a.name)));
    }

    // build model.json
    var model = new {
      name = "BilancioESG",
      version = "1.0.0",
      generated = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"),
      entities = entities.Select(e => new {
        name = e.name,
        attributes = e.attributes.Select(a => new { name = a.name, dataType = a.dataType, required = a.required }),
        partitions = new [] { new { location = $"entities/{e.name}.csv", fileFormat = "csv", refreshTime = (string?)null } }
      }),
      relationships = rels.Select(r => new { name=r.name, fromEntity=r.fromEntity, fromAttribute=r.fromAttribute, toEntity=r.toEntity, toAttribute=r.toAttribute }),
      annotations = new { description = "Common Data Model for ESG sustainability & carbon reporting (ESRS / GHG / IFRS S2)" }
    };

    var json = JsonSerializer.Serialize(model, new JsonSerializerOptions{ WriteIndented = true });
    File.WriteAllText(Path.Combine(root, "model.json"), json);

    Console.WriteLine($"CDM generated at: {root}");
    Console.WriteLine($"Entities: {entities.Count}, Relationships: {rels.Count}");
  }

  static Ent E(string name, List<Attr> attrs) => new Ent(name, attrs);
  static List<Attr> A(params (string n,string t,bool req)[] items)
    => items.Select(x => new Attr(x.n, x.t, x.req)).ToList();
  static Rel R(string name,string fromE,string fromA,string toE,string toA)
    => new Rel(name,fromE,fromA,toE,toA);
}
