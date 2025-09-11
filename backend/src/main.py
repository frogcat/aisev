from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import datasets, evaluations, qualitative_datasets, quantitative_datasets, ai_models, debug, migrate_sample_data, evaluation_results, scoring_dataset, custom_LLM_API

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(debug)
app.include_router(datasets)
app.include_router(evaluations)
app.include_router(qualitative_datasets)
app.include_router(quantitative_datasets)
app.include_router(ai_models)
app.include_router(migrate_sample_data)
app.include_router(evaluation_results.router)
app.include_router(scoring_dataset)
app.include_router(custom_LLM_API.router)
