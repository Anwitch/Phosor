"""Command-line interface for Phosor."""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from core.config import load_config, PhosorConfig
from core.file_scanner import scan_images
from core.face_engine import FaceEngine
from core.utils import build_face_dataset, save_embeddings, save_cluster_summary
from core.clustering import cluster_faces, build_cluster_summary
from core.folder_manager import materialize_clusters, create_cluster_representatives

app = typer.Typer(
    name="phosor",
    help="Phosor - Photo Sorting Orchestrator for Faces",
    add_completion=False,
)
console = Console()


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Configure logging for Phosor."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


@app.command()
def scan(
    input_dir: Optional[str] = typer.Option(
        None, "--input", "-i", help="Input folder with images"
    ),
    output_dir: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output folder for clusters"
    ),
    config: Optional[str] = typer.Option(
        "configs/config.toml", "--config", "-c", help="Path to config file"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Run without copying/moving files"
    ),
):
    """Run full Phosor pipeline: scan → embed → cluster → write output."""
    
    # Load configuration
    try:
        cfg = load_config(config)
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        raise typer.Exit(1)
    
    # Override config with CLI arguments
    if input_dir:
        cfg.input.dir = input_dir
    if output_dir:
        cfg.output.dir = output_dir
    
    # Setup logging
    setup_logging(cfg.logging.level, cfg.logging.file)
    logger = logging.getLogger(__name__)
    
    console.print("[bold blue]Phosor - Photo Sorting Orchestrator[/bold blue]")
    console.print(f"Input: {cfg.input.dir}")
    console.print(f"Output: {cfg.output.dir}")
    console.print(f"Mode: {cfg.output.mode}" + (" (DRY RUN)" if dry_run else ""))
    console.print()
    
    # Step 1: Scan image files
    console.print("[yellow]Step 1/6:[/yellow] Scanning images...")
    image_paths = scan_images(
        cfg.input.dir, cfg.input.recursive, cfg.input.min_file_size_kb
    )
    
    if not image_paths:
        console.print("[red]No images found! Check input directory.[/red]")
        raise typer.Exit(1)
    
    console.print(f"  Found {len(image_paths)} images\n")
    
    # Step 2: Initialize Face Engine
    console.print("[yellow]Step 2/6:[/yellow] Initializing face detection engine...")
    engine = FaceEngine()
    console.print("  Engine ready\n")
    
    # Step 3: Extract faces and embeddings
    console.print("[yellow]Step 3/6:[/yellow] Detecting faces and extracting embeddings...")
    faces = build_face_dataset(image_paths, engine)
    
    if not faces:
        console.print("[red]No faces detected in any image![/red]")
        raise typer.Exit(1)
    
    console.print(f"  Extracted {len(faces)} faces\n")
    
    # Step 4: Cluster faces
    console.print("[yellow]Step 4/6:[/yellow] Clustering faces...")
    faces = cluster_faces(
        faces,
        method=cfg.clustering.method,
        eps=cfg.clustering.eps,
        min_samples=cfg.clustering.min_samples,
    )
    summaries = build_cluster_summary(faces)
    
    # Filter small clusters
    summaries = [
        s for s in summaries 
        if s.num_faces >= cfg.clustering.min_faces_per_cluster
    ]
    
    console.print(f"  Found {len(summaries)} valid clusters\n")
    
    # Step 5: Organize files
    console.print("[yellow]Step 5/7:[/yellow] Organizing photos into folders...")
    materialize_clusters(
        faces, summaries, cfg.output.dir, mode=cfg.output.mode, dry_run=dry_run
    )
    console.print("  Files organized\n")
    
    # Step 5.5: Create representative images for each cluster
    if cfg.output.create_representatives:
        console.print("[yellow]Step 6/7:[/yellow] Creating representative face images...")
        create_cluster_representatives(
            faces, 
            summaries, 
            cfg.output.dir, 
            mode=cfg.output.representative_mode,
            dry_run=dry_run
        )
        console.print(f"  Created representatives (mode: {cfg.output.representative_mode})\n")
    
    # Step 6: Save metadata
    console.print("[yellow]Step 7/7:[/yellow] Saving metadata...")
    if cfg.handling.save_embeddings:
        save_embeddings(faces, f"{cfg.output.dir}/embeddings.json")
    save_cluster_summary(summaries, f"{cfg.output.dir}/clusters_summary.json")
    console.print("  Metadata saved\n")
    
    console.print("[bold green]✓ Pipeline complete![/bold green]")


@app.command()
def summary(
    metadata: str = typer.Argument(..., help="Path to clusters_summary.json"),
):
    """Display cluster summary from metadata file."""
    import json
    
    metadata_path = Path(metadata)
    if not metadata_path.exists():
        console.print(f"[red]File not found: {metadata}[/red]")
        raise typer.Exit(1)
    
    with open(metadata_path) as f:
        data = json.load(f)
    
    clusters = data.get("clusters", [])
    
    table = Table(title="Cluster Summary")
    table.add_column("Cluster ID", style="cyan")
    table.add_column("Label", style="magenta")
    table.add_column("Faces", justify="right", style="green")
    table.add_column("Unique Images", justify="right", style="yellow")
    
    for cluster in clusters:
        table.add_row(
            str(cluster["cluster_id"]),
            cluster["label"],
            str(cluster["num_faces"]),
            str(len(cluster["sample_images"])),
        )
    
    console.print(table)
    console.print(f"\nTotal clusters: {len(clusters)}")


if __name__ == "__main__":
    app()
