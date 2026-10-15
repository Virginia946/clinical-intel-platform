# Clinical Intelligence Platform

A data and AI platform for a fictional hospital, built on synthetic and public data.

v0.1: integrates four source systems (FHIR, object storage, openFDA, SharePoint)
into a tested Snowflake warehouse, transformed with dbt and orchestrated by Dagster.

All data is synthetic (Synthea, CMS DE-SynPUF) or public (openFDA).
No real patient data is used anywhere in this repository.
