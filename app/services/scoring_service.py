import asyncio
from app.db.config.database import SessionLocal
from app.db.models import Postulation
from app.services.score_engine import evaluar_postulacion
from app.services.ai_score_engine import evaluar_postulacion_ai

async def procesar_postulaciones(use_ai: bool = False):
    """
    Procesa todas las postulaciones que no tienen score_total asignado.
    Evalúa cada postulación y actualiza los scores en la base de datos.
    
    Args:
        use_ai (bool): Si True, usa el motor de IA. Si False, usa el motor de reglas.
    """
    async with SessionLocal() as session:
        # Buscar postulaciones sin score
        result = await session.execute(
            Postulation.__table__.select()
            .where(Postulation.score_total == None)
        )
        postulaciones = result.fetchall()

        print(f"Encontradas {len(postulaciones)} postulaciones para procesar.")
        print(f"Usando motor: {'IA' if use_ai else 'Reglas'}")

        for row in postulaciones:
            postulacion = row[0]
            
            # Extraer el texto de la respuesta abierta del payload JSON
            payload = postulacion.payload_json
            texto = ""
            
            # Buscar el campo de respuesta abierta en el payload
            if isinstance(payload, dict):
                # Buscar campos comunes que podrían contener la respuesta
                for key in ['respuesta_abierta', 'respuesta', 'texto', 'comentario', 'descripcion']:
                    if key in payload and payload[key]:
                        texto = str(payload[key])
                        break
                
                # Si no se encuentra, usar todo el payload como texto
                if not texto:
                    texto = str(payload)

            # Evaluar la postulación
            if use_ai:
                scores = await evaluar_postulacion_ai(texto)
            else:
                scores = evaluar_postulacion(texto)

            # Actualizar los scores
            postulacion.creatividad = scores["creatividad"]
            postulacion.claridad = scores["claridad"]
            postulacion.compromiso = scores["compromiso"]
            postulacion.score_total = scores["score_total"]

            session.add(postulacion)
            
            # Mostrar análisis si está disponible
            analisis = scores.get("analisis", "")
            print(f"Postulación {postulacion.id}: Creatividad={scores['creatividad']}, "
                  f"Claridad={scores['claridad']}, Compromiso={scores['compromiso']}, "
                  f"Total={scores['score_total']}")
            if analisis:
                print(f"  Análisis: {analisis}")

        await session.commit()
        print(f"Se procesaron {len(postulaciones)} postulaciones exitosamente.")

async def procesar_postulacion_especifica(postulacion_id: int, use_ai: bool = False):
    """
    Procesa una postulación específica por ID.
    
    Args:
        postulacion_id (int): ID de la postulación a procesar
        use_ai (bool): Si True, usa el motor de IA. Si False, usa el motor de reglas.
    """
    async with SessionLocal() as session:
        result = await session.execute(
            Postulation.__table__.select()
            .where(Postulation.id == postulacion_id)
        )
        postulacion_row = result.fetchone()
        
        if not postulacion_row:
            print(f"No se encontró la postulación con ID {postulacion_id}")
            return
        
        postulacion = postulacion_row[0]
        
        # Extraer texto del payload
        payload = postulacion.payload_json
        texto = ""
        
        if isinstance(payload, dict):
            for key in ['respuesta_abierta', 'respuesta', 'texto', 'comentario', 'descripcion']:
                if key in payload and payload[key]:
                    texto = str(payload[key])
                    break
            
            if not texto:
                texto = str(payload)

        # Evaluar
        if use_ai:
            scores = await evaluar_postulacion_ai(texto)
        else:
            scores = evaluar_postulacion(texto)
        
        # Actualizar
        postulacion.creatividad = scores["creatividad"]
        postulacion.claridad = scores["claridad"]
        postulacion.compromiso = scores["compromiso"]
        postulacion.score_total = scores["score_total"]

        session.add(postulacion)
        await session.commit()
        
        print(f"Postulación {postulacion_id} procesada:")
        print(f"  Creatividad: {scores['creatividad']}")
        print(f"  Claridad: {scores['claridad']}")
        print(f"  Compromiso: {scores['compromiso']}")
        print(f"  Score Total: {scores['score_total']}")
        
        # Mostrar análisis si está disponible
        analisis = scores.get("analisis", "")
        if analisis:
            print(f"  Análisis: {analisis}")
        
        return scores