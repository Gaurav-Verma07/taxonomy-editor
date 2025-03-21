from fastapi import HTTPException

from ..graph_db import get_current_transaction
from ..models.project_models import Project, ProjectCreate, ProjectEdit, ProjectStatus
from .node_controller import delete_project_nodes


async def get_project(project_id: str) -> Project:
    """
    Get project by id
    """
    query = """
    MATCH (p:PROJECT {id: $project_id})
    RETURN p
    """
    params = {"project_id": project_id}
    result = await get_current_transaction().run(query, params)
    project = await result.single()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project["p"])


async def get_projects_by_status(status: ProjectStatus) -> list[Project]:
    """
    Get projects by status
    """
    query = """
    MATCH (p:PROJECT {status: $status})
    RETURN p
    """
    params = {"status": status}
    result = await get_current_transaction().run(query, params)
    return [Project(**record["p"]) async for record in result]


async def create_project(project: ProjectCreate):
    """
    Create project
    """
    query = """
    CREATE (p:PROJECT $project) SET p.created_at = datetime()
    """
    params = {"project": project.model_dump()}
    await get_current_transaction().run(query, params)


async def edit_project(project_id: str, project_edit: ProjectEdit):
    """
    Edit project
    """
    query = """
    MATCH (p:PROJECT {id: $project_id})
    SET p += $project_edit
    """
    params = {
        "project_id": project_id,
        "project_edit": project_edit.model_dump(exclude_unset=True),
    }
    await get_current_transaction().run(query, params)


async def delete_project(project_id: str):
    """
    Delete project, its nodes and relationships
    """
    query = """
    MATCH (p:PROJECT {id: $project_id})
    DETACH DELETE p
    """
    params = {"project_id": project_id}
    await get_current_transaction().run(query, params)
    await delete_project_nodes(project_id)
