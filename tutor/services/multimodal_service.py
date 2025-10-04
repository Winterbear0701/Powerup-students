"""
Multimodal Service - Voice and Diagram Support
Handles speech-to-text, text-to-speech, and diagram generation
"""
import os
import hashlib
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class MultimodalService:
    """Service for multimodal interactions (voice, diagrams)"""
    
    def __init__(self):
        self.audio_dir = Path('media/audio')
        self.diagram_dir = Path('media/diagrams')
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.diagram_dir.mkdir(parents=True, exist_ok=True)
    
    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """
        Convert speech to text using Whisper
        
        Args:
            audio_file_path: Path to audio file
        
        Returns:
            Transcribed text or None
        """
        try:
            import whisper
            
            # Load Whisper model (use 'base' for speed, 'medium' for accuracy)
            model = whisper.load_model("base")
            
            # Transcribe
            result = model.transcribe(audio_file_path)
            text = result["text"]
            
            logger.info(f"Transcribed: {text[:50]}...")
            return text.strip()
            
        except ImportError:
            logger.error("Whisper not installed. Install with: pip install openai-whisper")
            return None
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    def text_to_speech(self, text: str, output_filename: Optional[str] = None) -> Optional[str]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            output_filename: Optional custom filename
        
        Returns:
            Path to generated audio file or None
        """
        try:
            from gtts import gTTS
            
            if not output_filename:
                # Generate filename from text hash
                text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
                output_filename = f"tts_{text_hash}.mp3"
            
            output_path = self.audio_dir / output_filename
            
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(str(output_path))
            
            logger.info(f"Generated audio: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.error("gTTS not installed. Install with: pip install gtts")
            return None
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    def generate_math_diagram(
        self,
        diagram_type: str,
        parameters: Dict,
        output_filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate mathematical diagrams using matplotlib
        
        Args:
            diagram_type: Type of diagram (graph, geometry, etc.)
            parameters: Parameters for the diagram
            output_filename: Optional custom filename
        
        Returns:
            Path to generated diagram or None
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            if not output_filename:
                diagram_hash = hashlib.md5(str(parameters).encode()).hexdigest()[:10]
                output_filename = f"diagram_{diagram_hash}.png"
            
            output_path = self.diagram_dir / output_filename
            
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Generate diagram based on type
            if diagram_type == 'function_graph':
                self._plot_function(ax, parameters)
            elif diagram_type == 'geometry':
                self._plot_geometry(ax, parameters)
            elif diagram_type == 'bar_chart':
                self._plot_bar_chart(ax, parameters)
            else:
                logger.warning(f"Unknown diagram type: {diagram_type}")
                plt.close(fig)
                return None
            
            plt.tight_layout()
            plt.savefig(str(output_path), dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Generated diagram: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.error("Matplotlib not installed. Install with: pip install matplotlib")
            return None
        except Exception as e:
            logger.error(f"Error generating diagram: {e}")
            return None
    
    def _plot_function(self, ax, params: Dict):
        """Plot a mathematical function"""
        import numpy as np
        
        # Default parameters
        x_range = params.get('x_range', (-10, 10))
        equation = params.get('equation', 'x**2')
        title = params.get('title', 'Function Graph')
        
        # Generate x values
        x = np.linspace(x_range[0], x_range[1], 500)
        
        try:
            # Evaluate equation
            y = eval(equation, {'x': x, 'np': np, 'sin': np.sin, 'cos': np.cos, 
                               'tan': np.tan, 'exp': np.exp, 'log': np.log})
            
            # Plot
            ax.plot(x, y, 'b-', linewidth=2, label=f'y = {equation}')
            ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
            ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_title(title)
            ax.legend()
            
        except Exception as e:
            logger.error(f"Error plotting function: {e}")
            ax.text(0.5, 0.5, 'Error plotting function', 
                   transform=ax.transAxes, ha='center')
    
    def _plot_geometry(self, ax, params: Dict):
        """Plot geometric shapes"""
        import numpy as np
        
        shape = params.get('shape', 'triangle')
        title = params.get('title', 'Geometric Shape')
        
        if shape == 'triangle':
            points = params.get('points', [[0, 0], [4, 0], [2, 3]])
            triangle = np.array(points + [points[0]])  # Close the triangle
            ax.plot(triangle[:, 0], triangle[:, 1], 'b-', linewidth=2, marker='o')
            ax.fill(triangle[:, 0], triangle[:, 1], alpha=0.3)
            
        elif shape == 'circle':
            radius = params.get('radius', 1)
            theta = np.linspace(0, 2*np.pi, 100)
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            ax.plot(x, y, 'b-', linewidth=2)
            ax.fill(x, y, alpha=0.3)
            
        elif shape == 'rectangle':
            width = params.get('width', 4)
            height = params.get('height', 3)
            rect = np.array([[0, 0], [width, 0], [width, height], [0, height], [0, 0]])
            ax.plot(rect[:, 0], rect[:, 1], 'b-', linewidth=2)
            ax.fill(rect[:, 0], rect[:, 1], alpha=0.3)
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(title)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
    
    def _plot_bar_chart(self, ax, params: Dict):
        """Plot a bar chart"""
        labels = params.get('labels', ['A', 'B', 'C', 'D'])
        values = params.get('values', [10, 20, 15, 25])
        title = params.get('title', 'Bar Chart')
        
        ax.bar(labels, values, color='steelblue', alpha=0.7)
        ax.set_xlabel(params.get('xlabel', 'Categories'))
        ax.set_ylabel(params.get('ylabel', 'Values'))
        ax.set_title(title)
        ax.grid(axis='y', alpha=0.3)
    
    def detect_diagram_need(self, query: str, response: str) -> Optional[Dict]:
        """
        Detect if a diagram would be helpful
        
        Args:
            query: User's question
            response: LLM's response
        
        Returns:
            Diagram parameters if needed, None otherwise
        """
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Geometry indicators
        geometry_keywords = ['triangle', 'circle', 'rectangle', 'square', 'angle', 
                           'shape', 'polygon', 'area', 'perimeter']
        if any(keyword in query_lower for keyword in geometry_keywords):
            return {
                'type': 'geometry',
                'shape': 'triangle',  # Default, should be detected more accurately
                'title': 'Geometric Figure'
            }
        
        # Graph indicators
        graph_keywords = ['graph', 'plot', 'function', 'equation', 'y = ', 'f(x)']
        if any(keyword in query_lower or keyword in response_lower for keyword in graph_keywords):
            return {
                'type': 'function_graph',
                'equation': 'x**2',  # Default, should be detected from response
                'title': 'Function Graph'
            }
        
        # Data visualization indicators
        data_keywords = ['chart', 'data', 'compare', 'statistics']
        if any(keyword in query_lower for keyword in data_keywords):
            return {
                'type': 'bar_chart',
                'title': 'Data Visualization'
            }
        
        return None


# Singleton instance
_multimodal_service_instance = None


def get_multimodal_service() -> MultimodalService:
    """Get or create multimodal service singleton"""
    global _multimodal_service_instance
    if _multimodal_service_instance is None:
        _multimodal_service_instance = MultimodalService()
    return _multimodal_service_instance
