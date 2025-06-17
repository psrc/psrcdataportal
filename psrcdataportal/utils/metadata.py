"""Metadata processing utilities for psrcdataportal package."""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

from ..exceptions import MetadataError
from ..utils.config import get_config_manager

logger = logging.getLogger(__name__)


class MetadataManager:
    """Manages metadata creation and updates for portal items."""
    
    def __init__(self) -> None:
        """Initialize the metadata manager."""
        self._config_manager = get_config_manager()
    
    def clean_metadata_string(self, text: Optional[str]) -> str:
        """Clean a string of any N/A's or None (NULL) values and wrap HTTP links in <a> tags.
        
        Args:
            text: A string to be cleaned.
            
        Returns:
            Cleaned string.
        """
        try:
            if text is None or text in ['N/A', 'nan', '']:
                return ''
            
            text = str(text)
            
            # URL pattern regex from guillaumepiot's gist at https://gist.github.com/guillaumepiot/4539986
            url_pattern = re.compile(
                r"(?i)((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]+[^\.\s])",
                re.MULTILINE | re.UNICODE
            )
            text = url_pattern.sub(r'<a href="\1" target="_blank">\1</a>', text)
            
            # Email pattern
            mailto_pattern = re.compile(
                r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)",
                re.MULTILINE | re.UNICODE
            )
            text = mailto_pattern.sub(r'<a href="mailto:\1">\1</a>', text)
            
            return text
            
        except Exception as e:
            logger.error(f"Failed to clean metadata string: {str(e)}")
            raise MetadataError("Failed to clean metadata string", str(e))
    
    def upsert_xml_element(
        self,
        parent_element: ET.Element,
        element_tag: str,
        element_text: str = ''
    ) -> ET.Element:
        """Look within parent_element for an element with element_tag.
        
        If found, updates its text value. If not found, adds it as a sub-element
        and updates its text.
        
        Args:
            parent_element: The XML element to search through.
            element_tag: The element tag to look for.
            element_text: The string to set the element's text property to.
            
        Returns:
            The new or existing element.
            
        Raises:
            MetadataError: If XML manipulation fails.
        """
        try:
            sub_element = parent_element.find(element_tag)
            
            if sub_element is None:
                new_element = ET.SubElement(parent_element, element_tag)
            else:
                new_element = parent_element.find(element_tag)
            
            if element_text and element_text.strip():
                new_element.text = element_text
            
            return new_element
            
        except Exception as e:
            logger.error(f"Failed to upsert XML element '{element_tag}': {str(e)}")
            raise MetadataError(f"Failed to upsert XML element '{element_tag}'", str(e))
    
    def initialize_metadata_file(self, output_path: Path) -> None:
        """Create a metadata XML file from a template.
        
        Args:
            output_path: Path where the metadata file should be created.
            
        Raises:
            MetadataError: If metadata file creation fails.
        """
        try:
            template_path = self._config_manager.get('paths.metadata_template')
            
            if not template_path or not Path(template_path).exists():
                # Create a basic metadata template if none exists
                self._create_basic_metadata_template(output_path)
            else:
                # Copy from template
                with open(template_path, 'r', encoding='utf-8') as template_file:
                    content = template_file.read()
                
                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(content)
            
            logger.debug(f"Initialized metadata file at {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize metadata file: {str(e)}")
            raise MetadataError("Failed to initialize metadata file", str(e))
    
    def _create_basic_metadata_template(self, output_path: Path) -> None:
        """Create a basic metadata XML template.
        
        Args:
            output_path: Path where the template should be created.
        """
        basic_template = '''<?xml version="1.0" encoding="UTF-8"?>
<metadata>
    <dataIdInfo>
        <idCitation>
            <resTitle></resTitle>
            <date>
                <pubDate></pubDate>
            </date>
            <citRespParty>
                <rpIndName></rpIndName>
                <rpOrgName></rpOrgName>
                <role>
                    <RoleCd value="006"/>
                </role>
                <rpCntInfo>
                    <cntAddress>
                        <eMailAdd></eMailAdd>
                        <delPoint></delPoint>
                        <city></city>
                        <adminArea></adminArea>
                        <postCode></postCode>
                    </cntAddress>
                    <cntPhone>
                        <voiceNum></voiceNum>
                    </cntPhone>
                    <cntOnlineRes>
                        <linkage></linkage>
                    </cntOnlineRes>
                </rpCntInfo>
            </citRespParty>
            <citOnlineRes>
                <linkage></linkage>
                <orName></orName>
            </citOnlineRes>
            <otherCitDet></otherCitDet>
        </idCitation>
        <idAbs></idAbs>
        <idCredit></idCredit>
        <suppInfo></suppInfo>
        <resMaint>
            <usrDefFreq>
                <duration></duration>
            </usrDefFreq>
        </resMaint>
        <resConst>
            <Consts>
                <useLimit></useLimit>
            </Consts>
        </resConst>
    </dataIdInfo>
    <mdContact>
        <rpIndName></rpIndName>
        <rpOrgName></rpOrgName>
        <rpCntInfo>
            <cntAddress>
                <eMailAdd></eMailAdd>
                <city></city>
                <postCode></postCode>
            </cntAddress>
            <cntPhone>
                <voiceNum></voiceNum>
            </cntPhone>
        </rpCntInfo>
    </mdContact>
    <dqInfo>
        <dataLineage>
            <statement></statement>
        </dataLineage>
    </dqInfo>
</metadata>'''
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(basic_template)
    
    def update_metadata_xml(
        self,
        metadata_file_path: Path,
        metadata_dict: Dict[str, Any],
        resource_properties: Dict[str, Any]
    ) -> None:
        """Update metadata XML file with provided metadata.
        
        Args:
            metadata_file_path: Path to the metadata XML file.
            metadata_dict: Dictionary containing metadata values.
            resource_properties: Dictionary containing resource properties.
            
        Raises:
            MetadataError: If metadata update fails.
        """
        try:
            if not metadata_file_path.exists():
                self.initialize_metadata_file(metadata_file_path)
            
            tree = ET.parse(metadata_file_path)
            root = tree.getroot()
            
            # Update main contact information
            self._update_contact_info(root, metadata_dict)
            
            # Update data identification info
            self._update_data_identification(root, metadata_dict, resource_properties)
            
            # Update constraints
            self._update_constraints(root, metadata_dict)
            
            # Update data quality info
            self._update_data_quality(root, metadata_dict)
            
            # Update field information if available
            if 'fields' in metadata_dict and metadata_dict['fields']:
                self._update_field_info(root, metadata_dict['fields'])
            
            # Write the updated XML
            tree.write(metadata_file_path, encoding='UTF-8', xml_declaration=True)
            logger.debug(f"Updated metadata file: {metadata_file_path}")
            
        except Exception as e:
            logger.error(f"Failed to update metadata XML: {str(e)}")
            raise MetadataError("Failed to update metadata XML", str(e))
    
    def _update_contact_info(self, root: ET.Element, metadata_dict: Dict[str, Any]) -> None:
        """Update contact information in metadata XML."""
        # Main contact
        md_contact = root.find('mdContact')
        if md_contact is not None:
            self.upsert_xml_element(md_contact, 'rpIndName', metadata_dict.get('contact_name', ''))
            self.upsert_xml_element(md_contact, 'rpOrgName', metadata_dict.get('organization_name', ''))
            
            rp_cnt_info = self.upsert_xml_element(md_contact, 'rpCntInfo')
            cnt_address = self.upsert_xml_element(rp_cnt_info, 'cntAddress')
            self.upsert_xml_element(cnt_address, 'eMailAdd', metadata_dict.get('contact_email', ''))
            self.upsert_xml_element(cnt_address, 'city', metadata_dict.get('contact_city', 'Seattle'))
            self.upsert_xml_element(cnt_address, 'postCode', str(metadata_dict.get('contact_zip', '98104')))
            
            cnt_phone = self.upsert_xml_element(rp_cnt_info, 'cntPhone')
            self.upsert_xml_element(cnt_phone, 'voiceNum', metadata_dict.get('contact_phone', ''))
    
    def _update_data_identification(
        self,
        root: ET.Element,
        metadata_dict: Dict[str, Any],
        resource_properties: Dict[str, Any]
    ) -> None:
        """Update data identification information in metadata XML."""
        data_id_info = root.find('dataIdInfo')
        if data_id_info is None:
            return
        
        # Citation information
        id_citation = self.upsert_xml_element(data_id_info, 'idCitation')
        self.upsert_xml_element(id_citation, 'resTitle', resource_properties.get('title', ''))
        
        # Publication date
        date_elem = self.upsert_xml_element(id_citation, 'date')
        self.upsert_xml_element(date_elem, 'pubDate', metadata_dict.get('date_last_updated', ''))
        
        # Responsible party
        cit_resp_party = self.upsert_xml_element(id_citation, 'citRespParty')
        self.upsert_xml_element(cit_resp_party, 'rpIndName', metadata_dict.get('contact_name', ''))
        self.upsert_xml_element(cit_resp_party, 'rpOrgName', 'Puget Sound Regional Council')
        
        role = self.upsert_xml_element(cit_resp_party, 'role')
        role_cd = self.upsert_xml_element(role, 'RoleCd')
        role_cd.set('value', '006')
        
        # Contact info for responsible party
        rp_cnt_info = self.upsert_xml_element(cit_resp_party, 'rpCntInfo')
        cnt_address = self.upsert_xml_element(rp_cnt_info, 'cntAddress')
        self.upsert_xml_element(cnt_address, 'eMailAdd', metadata_dict.get('contact_email', ''))
        self.upsert_xml_element(cnt_address, 'delPoint', metadata_dict.get('contact_street_address', ''))
        self.upsert_xml_element(cnt_address, 'city', metadata_dict.get('contact_city', ''))
        self.upsert_xml_element(cnt_address, 'adminArea', metadata_dict.get('contact_state', ''))
        self.upsert_xml_element(cnt_address, 'postCode', str(metadata_dict.get('contact_zip', '')))
        
        cnt_phone = self.upsert_xml_element(rp_cnt_info, 'cntPhone')
        self.upsert_xml_element(cnt_phone, 'voiceNum', metadata_dict.get('contact_phone', ''))
        
        cnt_online_res = self.upsert_xml_element(rp_cnt_info, 'cntOnlineRes')
        self.upsert_xml_element(cnt_online_res, 'linkage', metadata_dict.get('psrc_website', ''))
        
        # Online resource
        for existing_res in id_citation.findall('citOnlineRes'):
            id_citation.remove(existing_res)
        
        cit_online_res = self.upsert_xml_element(id_citation, 'citOnlineRes')
        self.upsert_xml_element(cit_online_res, 'linkage', metadata_dict.get('psrc_website', ''))
        self.upsert_xml_element(cit_online_res, 'orName', 'Data on PSRC Webpage')
        
        # Other citation details
        time_period_text = f"time period: {metadata_dict.get('time_period', '')}"
        self.upsert_xml_element(id_citation, 'otherCitDet', time_period_text)
        
        # Abstract
        abstract_parts = [
            self.clean_metadata_string(metadata_dict.get('summary', '')),
            self.clean_metadata_string(metadata_dict.get('summary_addendum', '')),
            self.clean_metadata_string(metadata_dict.get('summary_footer', ''))
        ]
        abstract = '<br/><br/>'.join(part for part in abstract_parts if part)
        self.upsert_xml_element(data_id_info, 'idAbs', abstract)
        
        # Credit
        self.upsert_xml_element(data_id_info, 'idCredit', metadata_dict.get('data_source', ''))
        
        # Supplemental info
        supp_info = self.clean_metadata_string(metadata_dict.get('supplemental_info', ''))
        self.upsert_xml_element(data_id_info, 'suppInfo', supp_info)
        
        # Maintenance info
        res_maint = self.upsert_xml_element(data_id_info, 'resMaint')
        usr_def_freq = self.upsert_xml_element(res_maint, 'usrDefFreq')
        self.upsert_xml_element(usr_def_freq, 'duration', metadata_dict.get('update_cadence', ''))
    
    def _update_constraints(self, root: ET.Element, metadata_dict: Dict[str, Any]) -> None:
        """Update constraint information in metadata XML."""
        data_id_info = root.find('dataIdInfo')
        if data_id_info is None:
            return
        
        # Remove existing constraints
        for existing_const in data_id_info.findall('resConst'):
            data_id_info.remove(existing_const)
        
        # Add new constraints
        res_const = ET.SubElement(data_id_info, 'resConst')
        consts = ET.SubElement(res_const, 'Consts')
        
        use_constraints = self.clean_metadata_string(metadata_dict.get('use_constraints', ''))
        self.upsert_xml_element(consts, 'useLimit', use_constraints)
    
    def _update_data_quality(self, root: ET.Element, metadata_dict: Dict[str, Any]) -> None:
        """Update data quality information in metadata XML."""
        dq_info = self.upsert_xml_element(root, 'dqInfo')
        data_lineage = self.upsert_xml_element(dq_info, 'dataLineage')
        
        lineage_text = self.clean_metadata_string(metadata_dict.get('data_lineage', ''))
        self.upsert_xml_element(data_lineage, 'statement', lineage_text)
    
    def _update_field_info(self, root: ET.Element, fields: List[Dict[str, Any]]) -> None:
        """Update field information in metadata XML."""
        # Remove existing field info
        for existing_ea in root.findall('eainfo'):
            root.remove(existing_ea)
        
        if not fields:
            return
        
        ea_info = ET.SubElement(root, 'eainfo')
        
        for field in fields:
            detailed = ET.SubElement(ea_info, 'detailed')
            enttyp = ET.SubElement(detailed, 'enttyp')
            
            self.upsert_xml_element(enttyp, 'enttypl', field.get('title', ''))
            self.upsert_xml_element(enttyp, 'enttypd', field.get('description', ''))


def build_field_mappings(df) -> List[Dict[str, str]]:
    """Build field mappings for ESRI-compatible data types.
    
    Args:
        df: DataFrame to analyze for field types.
        
    Returns:
        List of field mapping dictionaries.
        
    Raises:
        MetadataError: If field mapping fails.
    """
    try:
        dtypes = zip(df.columns, df.dtypes)
        type_translations = {
            "int64": "esriFieldTypeInteger",
            "object": "esriFieldTypeString",
            "float64": "esriFieldTypeDouble"
        }
        
        fields = []
        for column_name, dtype in dtypes:
            pd_type = str(dtype)
            
            # Special handling for certain columns
            if column_name in ['data_vintage', 'year_built']:
                field_type = "esriFieldTypeString"
            else:
                field_type = type_translations.get(pd_type, "esriFieldTypeString")
            
            fields.append({
                "name": column_name,
                "type": field_type
            })
        
        logger.debug(f"Built field mappings for {len(fields)} fields")
        return fields
        
    except Exception as e:
        logger.error(f"Failed to build field mappings: {str(e)}")
        raise MetadataError("Failed to build field mappings", str(e))
