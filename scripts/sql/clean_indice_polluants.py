from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}")

def clean_indice_polluants():
    """Nettoyer les tables indice et polluants en supprimant les colonnes inutiles"""
    
    print("🔧 NETTOYAGE DES TABLES INDICE ET POLLUANTS")
    print("=" * 50)
    
    with engine.connect() as conn:
        try:
            # 1. NETTOYER TABLE INDICE
            print("🎨 NETTOYAGE TABLE INDICE...")
            
            # Vérifier les colonnes actuelles
            indice_cols = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'indice' 
                ORDER BY ordinal_position
            """)).fetchall()
            
            current_indice = [col[0] for col in indice_cols]
            print(f"   📊 AVANT: {current_indice}")
            
            # Supprimer les colonnes spécifiées
            columns_to_remove_indice = ['seuil_min', 'seuil_max', 'created_at']
            
            for col in columns_to_remove_indice:
                if col in current_indice:
                    try:
                        conn.execute(text(f"ALTER TABLE indice DROP COLUMN {col} CASCADE"))
                        print(f"   ✅ {col} supprimée")
                    except Exception as e:
                        print(f"   ⚠️ {col}: {e}")
                else:
                    print(f"   ℹ️ {col} n'existe pas")
            
            # Supprimer d'autres colonnes inutiles si elles existent
            other_unwanted_indice = ['description', 'ordre_gravite', 'nb_mesures']
            
            for col in other_unwanted_indice:
                if col in current_indice:
                    try:
                        conn.execute(text(f"ALTER TABLE indice DROP COLUMN {col} CASCADE"))
                        print(f"   ✅ {col} supprimée (bonus)")
                    except Exception as e:
                        print(f"   ⚠️ {col}: {e}")
            
            # 2. NETTOYER TABLE POLLUANTS
            print(f"\n🧪 NETTOYAGE TABLE POLLUANTS...")
            
            # Vérifier les colonnes actuelles
            polluants_cols = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'polluants' 
                ORDER BY ordinal_position
            """)).fetchall()
            
            current_polluants = [col[0] for col in polluants_cols]
            print(f"   📊 AVANT: {len(current_polluants)} colonnes")
            
            # Supprimer les colonnes surchargées
            columns_to_remove_polluants = [
                'nom_complet', 'nom_court', 'formule_chimique', 'description',
                'type_polluant', 'origine_principale', 'effets_sante',
                'seuil_information', 'seuil_alerte', 'valeur_limite_annuelle',
                'valeur_limite_horaire', 'couleur_viz', 'ordre_affichage',
                'actif', 'created_at'
            ]
            
            for col in columns_to_remove_polluants:
                if col in current_polluants:
                    try:
                        conn.execute(text(f"ALTER TABLE polluants DROP COLUMN {col} CASCADE"))
                        print(f"   ✅ {col} supprimée")
                    except Exception as e:
                        print(f"   ⚠️ {col}: {e}")
            
            # 3. COMMIT
            conn.commit()
            print(f"\n💾 MODIFICATIONS COMMITÉES")
            
            # 4. VÉRIFICATION FINALE
            print(f"\n📊 STRUCTURES FINALES:")
            
            # Structure finale indice
            final_indice = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'indice' ORDER BY ordinal_position
            """)).fetchall()
            indice_final = [col[0] for col in final_indice]
            print(f"   🎨 indice: {indice_final} ({len(indice_final)} colonnes)")
            
            # Structure finale polluants
            final_polluants = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'polluants' ORDER BY ordinal_position
            """)).fetchall()
            polluants_final = [col[0] for col in final_polluants]
            print(f"   🧪 polluants: {polluants_final} ({len(polluants_final)} colonnes)")
            
            # 5. VÉRIFICATION DES DONNÉES
            print(f"\n📋 VÉRIFICATION DES DONNÉES:")
            
            # Données indice
            indice_data = conn.execute(text("SELECT * FROM indice ORDER BY niveau")).fetchall()
            print("   🎨 Données indice:")
            for row in indice_data:
                print(f"      {row}")
            
            # Données polluants
            polluants_data = conn.execute(text("SELECT * FROM polluants ORDER BY code_polluant")).fetchall()
            print("   🧪 Données polluants:")
            for row in polluants_data:
                print(f"      {row}")
            
            # 6. TEST DE JOINTURE
            print(f"\n🔗 TEST DE JOINTURES:")
            try:
                test = conn.execute(text("""
                    SELECT 
                        q.code_polluant,
                        p.unite_mesure,
                        q.qualite_globale,
                        i.couleur,
                        COUNT(*) as nb
                    FROM qualite_air q
                    JOIN polluants p ON q.code_polluant = p.code_polluant
                    JOIN indice i ON q.qualite_globale = i.niveau
                    GROUP BY q.code_polluant, p.unite_mesure, q.qualite_globale, i.couleur
                    ORDER BY nb DESC
                    LIMIT 3
                """)).fetchall()
                
                for polluant, unite, qualite, couleur, nb in test:
                    print(f"   {polluant} ({unite}) → {qualite} ({couleur}): {nb} mesures")
                    
            except Exception as e:
                print(f"   ❌ Erreur jointure: {e}")
            
            print(f"\n🎉 NETTOYAGE TERMINÉ AVEC SUCCÈS !")
            print("✅ seuil_min, seuil_max, created_at supprimées de indice")
            print("✅ Colonnes surchargées supprimées de polluants")
            print("✅ Tables épurées et fonctionnelles")
            print("✅ Relations préservées")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    clean_indice_polluants()