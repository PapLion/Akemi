# Compuertas actuales

| Compuerta | Estado |
| --- | --- |
| corpus_located | True |
| all_selected_release_shards_verified | True |
| selected_documents_integrity | True |
| selected_rights | True |
| selected_exact_dedup | True |
| selected_family_split | True |
| selected_5M_independent_targets | False |
| approved_spanish_available | False |
| global_web_rights_closed | False |
| global_near_duplicate_recall_certified | False |
| global_benchmark_contamination_closed | False |
| V3_compatible_deterministic | True |
| V3_whole_corpus_count_complete | False |
| F2_implemented_causal | True |
| baseline_available | True |
| trainer_resume_technical | True |
| final_dataset_reader_resume_certified | False |
| CPU_benchmark | True |
| future_evaluation_frozen | True |
| full_training_started | False |
| GPU_or_money_used | False |
| decision | BLOCKED by approved diverse independent data volume and clearance, not missing corpus. Technical preflight is ready; no authorization to train5M. |

El candidato y baseline existen; la selección final para5Mno. Falta cerrar derechos y preservar atribución de un subconjunto del corpus recuperado, dedup y separación porfamilias/versiones, validar español/código/prosa, contar exactamente sus targets y conectar el lector final con checkpoint de orden/manifiesto. El conteo totalV3 del maestro puede continuar aparte; no es sustituto del permiso ni requisito de acabar todo antes de un subconjunto aprobado.

Referencias de benchmarks globales siguen sinclearance: evaluation_references histórico vacío; no se abrieron sellados. La ausencia de coincidencias no se convierte enPASS. [Evaluación futura congelada](EVALUATION_PROTOCOL.md). Configuración prospectiva enF2_CONFIG.json; `training_authorized=false`, no hay ejecución5M.
