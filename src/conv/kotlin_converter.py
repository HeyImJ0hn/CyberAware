import os
from dao.gradle_con import GradleCon
from utils.text_utils import TextUtils

class KotlinConverter:
    
    @staticmethod
    def convert_to_kotlin(game, logger, signed, keystore):
        game_name = game.game_name
        entities = game.get_entities()
        entities = []
        
        
        # App Screens
        app_nav_file = f'''package dev.cyberaware.{TextUtils.clean_text(game_name)}.navigation

import androidx.activity.compose.BackHandler
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import dev.cyberaware.{TextUtils.clean_text(game_name)}.R
import dev.cyberaware.{TextUtils.clean_text(game_name)}.screens.BaseScreen
import dev.cyberaware.{TextUtils.clean_text(game_name)}.screens.HomeScreen
import dev.cyberaware.{TextUtils.clean_text(game_name)}.screens.OptionButton

@Composable
fun AppNavigation() {{
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {{
        composable("home") {{
            HomeScreen(
                onNavigateToBaseScreen = {{ screenId ->
                    navController.navigate("base/$screenId")
                }}
            )
        }}

        composable(
            "base/{{screenId}}",
            arguments = listOf(navArgument("screenId") {{ type = NavType.StringType }})
        ) {{ backStackEntry ->
            BackHandler(true) {{
                // Do nothing
            }}

            val screenId = backStackEntry.arguments?.getString("screenId") ?: return@composable
            when (screenId) {{
        '''
        for entity in entities:
            string = f'"{entity.id}" -> BaseScreen(\n\
                screenId=screenId, "{entity.text}", true, R.drawable.pexels, buttons = listOf('
            
            for option in entity.options:
                string += f'{{modifier -> OptionButton(modifier, "{option.text}") {{ navController.navigate("base/{str(option.entity.id)}") }} }},'
                
            string += f'))'
        app_nav_file +='''
            }
        }
    }
}
        '''
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'navigation', 'AppNavigation.kt')
        with open(file_path, 'w') as file:
            file.write(app_nav_file)
            
            
            
            
        # Change app name in strings.xml
        strings_file = f'''<resources>
    <string name="app_name">{game_name}</string>
    <string name="title_activity_home_screen">HomeScreen</string>
    <string name="title_activity_app_navigation">AppNavigation</string>
</resources>
        '''
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'android', 'app', 'src', 'main', 'res', 'values', 'strings.xml')
        with open(file_path, 'w') as file:
            file.write(strings_file)
            
            
            
            
        # Change app name in settings.gradle.kts
        settings_file = f'''pluginManagement {{
    repositories {{
        google {{
            content {{
                includeGroupByRegex("com\\\\.android.*")
                includeGroupByRegex("com\\\\.google.*")
                includeGroupByRegex("androidx.*")
            }}
        }}
        mavenCentral()
        gradlePluginPortal()
    }}
}}
dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {{
        google()
        mavenCentral()
    }}
}}

rootProject.name = "{TextUtils.clean_text(game_name)}"
include(":app")
        '''
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'android', 'settings.gradle.kts')
        with open(file_path, 'w') as file:
            file.write(settings_file)
        
        
        
        # Change app name in build.gradle.kts
        build_file = f'''plugins {{
    alias(libs.plugins.android.application)
    alias(libs.plugins.jetbrains.kotlin.android)
}}

android {{
    namespace = "dev.cyberaware.{TextUtils.clean_text(game_name)}"
    compileSdk = 34

    defaultConfig {{
        applicationId = "dev.cyberaware.{TextUtils.clean_text(game_name)}"
        minSdk = 26
        targetSdk = 34
        versionCode = {game.app_version}
        versionName = "{game.app_version}.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {{
            useSupportLibrary = true
        }}
    }}

    buildTypes {{
        release {{
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }}
    }}
    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }}
    kotlinOptions {{
        jvmTarget = "1.8"
    }}
    buildFeatures {{
        compose = true
    }}
    composeOptions {{
        kotlinCompilerExtensionVersion = "1.5.1"
    }}
    packaging {{
        resources {{
            excludes += "/META-INF/{{AL2.0,LGPL2.1}}"
        }}
    }}
}}

dependencies {{

    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)

    implementation("androidx.compose.ui:ui:1.6.7")
    implementation("androidx.navigation:navigation-compose:2.7.7")

    implementation("com.google.android.exoplayer:exoplayer:2.19.1")
    implementation("androidx.media3:media3-exoplayer:1.3.1")
    implementation("androidx.media3:media3-ui:1.3.1")
}}'''    

        file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'android', 'app', 'build.gradle.kts')
        with open(file_path, 'w') as file:
            file.write(build_file)
            
            
            
            
        # MainActivity.kt
        main_activity_file = f'''package dev.cyberaware.{TextUtils.clean_text(game_name)}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import dev.jpires.{TextUtils.clean_text(game_name)}.navigation.AppNavigation
import dev.jpires.{TextUtils.clean_text(game_name)}.ui.theme.CyberAwareBaseAppTheme

class MainActivity : ComponentActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)

        setContent {{
            CyberAwareBaseAppTheme {{
                Surface(color = MaterialTheme.colorScheme.background) {{
                   AppNavigation()
                }}
            }}
        }}
    }}
}}
        '''
        
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'MainActivity.kt')
        with open(file_path, 'w') as file:
            file.write(main_activity_file)
            
        
        GradleCon.compile(logger, signed, keystore)